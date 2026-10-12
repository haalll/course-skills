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

# ---- database-bound guards (r14). `run(cypher, **params)` must return (rows, stats) and raise on a server error. Checked against local Neo4j 5.26.14 in lab/n23/d3_guard_checks.py.
CSV_NAME = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}")
class ConstructionStopped(Exception): pass

def rel_load_checked(run, csv, a, a_key, b, b_key, rel, from_col, to_col):
    """Load relationships from a CSV whose rows name both ends. MATCH drops a row whose end is missing and says nothing, so compare DISTINCT pairs
    (MERGE collapses repeats; raw rows would cry wolf): before the write, resolvable pairs must equal pairs in the file; after, each pair must have the edge."""
    if not CSV_NAME.fullmatch(csv): raise ValueError(f"unsafe file name {csv!r}")
    f, t = f"row.{ident(from_col)}", f"row.{ident(to_col)}"
    src = f"LOAD CSV WITH HEADERS FROM 'file:///{csv}' AS row"
    ends = f"MATCH (a:{ident(a)} {{{ident(a_key)}: {f}}}) MATCH (b:{ident(b)} {{{ident(b_key)}: {t}}})"
    pairs = run(f"{src} RETURN count(DISTINCT [{f}, {t}])")[0][0][0]
    found = run(f"{src} {ends} RETURN count(DISTINCT [{f}, {t}])")[0][0][0]
    if found != pairs: raise ConstructionStopped(f"{pairs - found} of {pairs} distinct pairs have a missing end; nothing written")
    _, st = run(f"{src} {ends} MERGE (a)-[:{ident(rel)}]->(b)")
    done = run(f"{src} {ends.replace(') MATCH (b:', ')-[:' + ident(rel) + ']->(b:', 1)} RETURN count(DISTINCT [{f}, {t}])")[0][0][0]
    if done != pairs: raise ConstructionStopped(f"{done} of {pairs} distinct pairs have the {rel} edge after the load")
    return {"rows_distinct_pairs": pairs, "relationships_created": st.get("relationships_created", 0)}

def constraint_or_stop(run, label, key):
    """The constraint step must stop the loader when it fails: IF NOT EXISTS still raises when existing rows break it."""
    try: run(constraint_safe(label, key))
    except Exception as e: raise ConstructionStopped(f"constraint on {label}.{key} failed, no load: {str(e)[:80]}") from e

def link_unique(run, ent, cand, max_dist, same_prop=None):
    """Link an entity to a candidate only when exactly ONE candidate is under max_dist (APOC jaroWinklerDistance: 0-1, lower = closer) and, if same_prop is
    given, that candidate also has an equal, non-null second property. A distance alone links near names, not same things, and a lone near name is
    still a wrong link; the rest stay unlinked for review."""
    if not isinstance(max_dist, (int, float)) or not 0 < max_dist <= 1: raise ValueError("max_dist is a 0-1 distance")
    extra = f" AND e.{ident(same_prop)} IS NOT NULL AND e.{ident(same_prop)} = p.{ident(same_prop)}" if same_prop else ""
    q = (f"MATCH (e:{ident(ent)}) CALL {{ WITH e MATCH (p:{ident(cand)}) WITH p, apoc.text.jaroWinklerDistance(e.name, p.name) AS d "
         f"WHERE d < $m RETURN collect(p) AS near }} WITH e, near WHERE size(near) = 1 WITH e, near[0] AS p WHERE true{extra} "
         f"MERGE (e)-[:CORRESPONDS_TO]->(p)")
    return run(q, m=max_dist)[1].get("relationships_created", 0)
