"""Reference sketch (our own wording): identifier guard for string-built Cypher, a markdown splitter and title finder that respect front matter and code fences,
and a key normaliser that strips a label prefix only at a word boundary. Checked in lab/n22/n22_checks.py (no database). Python 3, standard library only.
"""
import re

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,63}")
def ident(x):
    if not isinstance(x, str) or not IDENT.fullmatch(x): raise ValueError(f"unsafe identifier {x!r}")
    return f"`{x}`"
def constraint_safe(label, key): return f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{ident(label)}) REQUIRE n.{ident(key)} IS UNIQUE"

def split_safe(md):
    lines, chunks, cur, fence, i = md.split("\n"), [], [], False, 0
    if lines and lines[0].strip() == "---":                    # front matter: a leading '---' ... '---' block is metadata, not a page break
        for j in range(1, len(lines)):
            if lines[j].strip() == "---": i = j + 1; break
    for ln in lines[i:]:
        if ln.lstrip().startswith("```"): fence = not fence
        if ln.strip() == "---" and not fence: chunks.append("\n".join(cur).strip()); cur = []
        else: cur.append(ln)
    chunks.append("\n".join(cur).strip()); return [c for c in chunks if c]
def title_safe(md, fallback):
    fence = False
    for ln in split_safe_lines(md):
        if ln.lstrip().startswith("```"): fence = not fence
        elif not fence and ln.startswith("# "): return ln[2:].strip()
    return fallback
def split_safe_lines(md):
    lines = md.split("\n")
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---": return lines[j + 1:]
    return lines

def norm_safe(key, label):             # strip the prefix only at a word boundary
    k = key.strip().lower(); l = label.lower()
    return re.sub(rf"^{re.escape(l)}[_\s]+", "", k)
