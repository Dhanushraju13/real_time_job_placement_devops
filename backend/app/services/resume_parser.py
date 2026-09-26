import io
import re
from typing import List, Union, BinaryIO
from pathlib import Path
import pypdf

# Canonical skill representations and regex patterns
SKILL_PATTERNS = [
    # Multi-word or special-symbol skills (checked first)
    ("C++", r"(?<![a-zA-Z0-9_])c\+\+(?![a-zA-Z0-9_])"),
    ("C#", r"(?<![a-zA-Z0-9_])c#(?![a-zA-Z0-9_])"),
    ("Spring Boot", r"\bspring\s+boot\b"),
    ("REST API", r"\brest(?:ful)?(?:\s+api)?\b"),
    ("Machine Learning", r"\bmachine\s+learning\b"),
    ("Node.js", r"\bnode(?:\.js)?\b"),
    ("React", r"\breact(?:\.js)?\b"),
    ("Next.js", r"\bnext(?:\.js)?\b"),
    ("Express", r"\bexpress(?:\.js)?\b"),
    ("PostgreSQL", r"\bpostgres(?:ql)?\b"),
    ("MongoDB", r"\bmongo(?:db)?\b"),
    ("MySQL", r"\bmysql\b"),
    ("CI/CD", r"\bci[\s/-]?cd\b"),
    ("Kubernetes", r"\b(?:kubernetes|k8s)\b"),
    ("JavaScript", r"\bjavascript\b"),
    ("TypeScript", r"\btypescript\b"),
    # Exact word match for single-word technologies
    ("Java", r"\bjava\b"),
    ("Python", r"\bpython\b"),
    ("FastAPI", r"\bfastapi\b"),
    ("Flask", r"\bflask\b"),
    ("Django", r"\bdjango\b"),
    ("SQL", r"\bsql\b"),
    ("Redis", r"\bredis\b"),
    ("Docker", r"\bdocker\b"),
    ("Jenkins", r"\bjenkins\b"),
    ("Git", r"\bgit\b"),
    ("GitHub", r"\bgithub\b"),
    ("AWS", r"\baws\b"),
    ("Azure", r"\bazure\b"),
    ("HTML", r"\bhtml(?:5)?\b"),
    ("CSS", r"\bcss(?:3)?\b"),
    ("TensorFlow", r"\btensorflow\b"),
    ("PyTorch", r"\bpytorch\b"),
    ("Linux", r"\blinux\b"),
    ("GraphQL", r"\bgraphql\b"),
    # Single letter "C" strictly bounded
    ("C", r"(?<![a-zA-Z0-9_#+])c(?![a-zA-Z0-9_#+])"),
]

def extract_text_from_pdf(source: Union[str, Path, bytes, BinaryIO]) -> str:
    """
    Extract raw text from a PDF file path, raw bytes, or file stream.
    """
    if isinstance(source, (str, Path)):
        reader = pypdf.PdfReader(str(source))
    elif isinstance(source, bytes):
        reader = pypdf.PdfReader(io.BytesIO(source))
    else:
        reader = pypdf.PdfReader(source)

    text_parts = []
    for page in reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        except Exception:
            continue

    return " ".join(text_parts)

def extract_skills(text: str) -> List[str]:
    """
    Scan normalized text and detect skills based on the controlled dictionary.
    Returns deduplicated, sorted list of canonical skill names.
    """
    if not text:
        return []

    # Normalize whitespace
    normalized = " " + text.lower() + " "
    detected = set()

    for canonical_name, pattern in SKILL_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            detected.add(canonical_name)

    return sorted(list(detected))

def parse_resume(source: Union[str, Path, bytes, BinaryIO]) -> dict:
    """
    Extracts text and identified skills from a given PDF resume.
    """
    text = extract_text_from_pdf(source)
    skills = extract_skills(text)
    return {
        "text_length": len(text),
        "skills": skills
    }
