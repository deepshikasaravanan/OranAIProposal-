from typing import List
import pdfplumber, fitz, os, re
from docx import Document as DocxDocument
from .schema import ShallReq, RequirementGraph
from .utils import stable_id

SHALL_RE = re.compile(r'\bshall\b', re.IGNORECASE)

def extract_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        # Try PyMuPDF first
        try:
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception:
            text = ""
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
    elif ext == ".docx":
        d = DocxDocument(path)
        return "\n".join([p.text for p in d.paragraphs])
    else:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

def naive_section_for(line: str) -> str:
    m = re.search(r'(\d+\.\d+(?:\.\d+)*)', line)
    return m.group(1) if m else ""

def extract_shalls_offline(text: str) -> List[ShallReq]:
    shalls: List[ShallReq] = []
    for line in re.split(r'[\n\r]+', text):
        if SHALL_RE.search(line) and len(line.strip()) > 20:
            sec = naive_section_for(line)
            sid = stable_id(line.strip())
            shalls.append(ShallReq(id=sid, section=sec, text=line.strip()))
    return shalls

def parse_pws(path: str) -> RequirementGraph:
    raw = extract_text(path)
    shalls = extract_shalls_offline(raw)
    return RequirementGraph(meta={"source": path}, shalls=shalls, edges=[])
