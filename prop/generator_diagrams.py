"""Mermaid diagram rendering utilities (Prompt 8).

Provides render_mermaid_to_png(mermaid_text) -> bytes.

Primary method: use mermaid-cli (mmdc) if available in PATH.
Fallback: simple text rendering via matplotlib so documents still build
even when mermaid-cli is not installed.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from io import BytesIO
from typing import Optional


def _which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def _render_with_mmdc(src: str) -> bytes:
    mmdc = _which("mmdc")
    if not mmdc:
        raise FileNotFoundError("mmdc (mermaid-cli) not found in PATH")
    with tempfile.TemporaryDirectory() as td:
        in_path = os.path.join(td, "diagram.mmd")
        out_path = os.path.join(td, "diagram.png")
        with open(in_path, "w", encoding="utf-8") as f:
            f.write(src)
        cmd = [mmdc, "-i", in_path, "-o", out_path, "-b", "transparent"]
        try:
            subprocess.run(cmd, check=True, timeout=30, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"mmdc failed: {e.stderr.decode('utf-8', 'ignore')[:400]}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("mmdc timed out")
        if not os.path.exists(out_path):
            raise RuntimeError("mmdc did not produce output")
        return open(out_path, "rb").read()


def _render_fallback(src: str) -> bytes:
    """Fallback renderer: write diagram text into a PNG using matplotlib."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # ensure headless
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(6, 2 + min(6, 0.15 * src.count('\n'))))
        plt.axis('off')
        plt.text(0.01, 0.99, src[:4000], va='top', ha='left', family='monospace', fontsize=8, wrap=True)
        bio = BytesIO()
        plt.savefig(bio, format='png', dpi=160, bbox_inches='tight')
        plt.close(fig)
        bio.seek(0)
        return bio.read()
    except Exception:
        # Absolute minimal 1x1 PNG fallback (transparent)
        return bytes.fromhex(
            '89504E470D0A1A0A0000000D4948445200000001000000010806000000' \
            '1F15C4890000000A49444154789C6360000002000100' \
            '05FE02FEA74A650000000049454E44AE426082'
        )


def render_mermaid_to_png(mermaid_text: str) -> bytes:
    """Render Mermaid definition to PNG bytes.

    Attempts mermaid-cli first; falls back to text snapshot.
    """
    try:
        return _render_with_mmdc(mermaid_text)
    except Exception:
        return _render_fallback(mermaid_text)


__all__ = ["render_mermaid_to_png"]
