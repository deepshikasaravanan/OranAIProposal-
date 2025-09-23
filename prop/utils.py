import os
import re
import tempfile
import json
import hashlib
from datetime import datetime, timezone
from typing import List, Optional, Any

try:
    from dateutil import parser as dateparser  # type: ignore
except Exception:  # fallback
    dateparser = None

def env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(name, default)

def parse_date_any(s: str) -> Optional[datetime]:
    if not s:
        return None
    if dateparser:
        try:
            return dateparser.parse(s)
        except Exception:
            pass
    # Simple fallbacks
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None

def days_until(d: Optional[datetime]) -> int:
    if not d:
        return 12
    now = datetime.now(timezone.utc)
    if not d.tzinfo:
        d = d.replace(tzinfo=timezone.utc)
    return max(0, (d - now).days)

def download_s3_to_temp(uri: str) -> Optional[str]:
    # s3://bucket/key
    try:
        import boto3  # type: ignore
    except Exception:
        return None
    m = re.match(r"s3://([^/]+)/(.+)", uri)
    if not m:
        return None
    bucket, key = m.group(1), m.group(2)
    tmp = tempfile.mkstemp(prefix="s3_", suffix=os.path.splitext(key)[1])[1]
    s3 = boto3.client("s3", region_name=env("AWS_REGION"))
    s3.download_file(bucket, key, tmp)
    return tmp

def materialize_paths(paths: List[str]) -> List[str]:
    out = []
    for p in paths:
        if p.startswith("s3://"):
            local = download_s3_to_temp(p)
            if local:
                out.append(local)
        elif os.path.exists(p):
            out.append(p)
    return out

def extract_text_quick(path: str) -> str:
    txt = ""
    try:
        if path.lower().endswith(".pdf"):
            import fitz  # PyMuPDF
            with fitz.open(path) as doc:
                for page in doc:
                    txt += page.get_text("text") + "\n"
        elif path.lower().endswith((".docx",)):
            from docx import Document
            doc = Document(path)
            txt = "\n".join(p.text for p in doc.paragraphs)
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
    except Exception:
        pass
    return txt

CAPABILITY_TAXONOMY = {
    "ai": ["artificial intelligence", "ai", "ml", "machine learning"],
    "ml": ["machine learning", "ml"],
    "devops": ["devops", "cicd", "pipeline"],
    "cloud": ["aws", "azure", "cloud", "gcp"],
    "cyber": ["zero trust", "cisa", "nist", "cyber", "security"],
    "data_engineering": ["etl", "data pipeline", "spark", "airflow", "dbt"],
}

def infer_capabilities(text: str) -> List[str]:
    text_l = text.lower()
    caps = []
    for cap, keys in CAPABILITY_TAXONOMY.items():
        if any(k in text_l for k in keys):
            caps.append(cap)
    return caps

def slugify(s: str) -> str:
    s = re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-')
    return s.lower()

def stable_id(text: str) -> str:
    return hashlib.sha1(text.encode('utf-8')).hexdigest()[:10]

def read_text(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_json(path: str, data: Any):
    dirpath = os.path.dirname(path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
