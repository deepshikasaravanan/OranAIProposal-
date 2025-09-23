"""S3 and ZIP file helper utilities.

Contracts:
- is_s3(uri: str) -> bool
- download_to_tmp(uri_or_path: str) -> str
- list_from_zip(path: str) -> list[str]

Design:
- Do not hardcode credentials. boto3 will use env / IAM role / shared config.
- Functions are resilient: raise only on obvious misuse (bad path / unsupported scheme),
  otherwise attempt best-effort and log.
"""
from __future__ import annotations
import os
import re
import tempfile
import shutil
import zipfile
import logging
from typing import List

log = logging.getLogger(__name__)
_S3_RE = re.compile(r"^s3://([^/]+)/(.+)$")

try:
    import boto3  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    boto3 = None  # type: ignore


def is_s3(uri: str) -> bool:
    """Return True if the string looks like an s3 URI (s3://bucket/key)."""
    if not isinstance(uri, str):
        return False
    return bool(_S3_RE.match(uri.strip()))


def _download_s3(uri: str) -> str:
    if not boto3:  # pragma: no cover - environment without boto3
        raise RuntimeError("boto3 not available to download S3 object")
    m = _S3_RE.match(uri)
    if not m:
        raise ValueError(f"Not a valid s3 uri: {uri}")
    bucket, key = m.group(1), m.group(2)
    suffix = os.path.splitext(key)[1] or ""
    fd, tmp_path = tempfile.mkstemp(prefix="s3dl_", suffix=suffix)
    os.close(fd)
    log.info("Downloading s3://%s/%s to %s", bucket, key, tmp_path)
    s3 = boto3.client("s3")
    s3.download_file(bucket, key, tmp_path)
    return tmp_path


def download_to_tmp(uri_or_path: str) -> str:
    """Materialize a local path: if s3 URI download to temp; else return absolute path.

    Raises:
        FileNotFoundError: if local path does not exist.
        RuntimeError: if boto3 missing for s3 download.
    """
    if is_s3(uri_or_path):
        return _download_s3(uri_or_path)
    abspath = os.path.abspath(uri_or_path)
    if not os.path.exists(abspath):
        raise FileNotFoundError(abspath)
    return abspath


def list_from_zip(path: str) -> List[str]:
    """Extract a zip archive to a temp directory and return a list of extracted file paths.

    Notes:
        - Skips directories.
        - Caller is responsible for cleanup if persistence is required. Temp folder is returned
          only indirectly via each file path prefix.
    """
    ap = download_to_tmp(path)
    if not zipfile.is_zipfile(ap):
        raise ValueError(f"Not a zip file: {ap}")
    out_dir = tempfile.mkdtemp(prefix="unz_")
    files: List[str] = []
    with zipfile.ZipFile(ap) as z:
        for name in z.namelist():
            if name.endswith('/'):
                continue
            target = os.path.join(out_dir, name)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with z.open(name) as src, open(target, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            files.append(target)
    log.info("Extracted %d files from %s into %s", len(files), ap, out_dir)
    return files

__all__ = ["is_s3", "download_to_tmp", "list_from_zip"]
