---
name: agentic-kg-safe-construction
description: Use when an approved plan (node rules, relationship rules, entity types) is turned into database writes by code: building Cypher from model-written labels, LOAD CSV / MERGE loads that can drop rows silently, constraint steps, markdown splitting, similarity-threshold entity linking and re-running ingestion; checks run on a local Neo4j 5.26.14 and in Python.
---

# Deterministic construction from an approved plan (DRAFT; local Neo4j 5.26.14, tiny data). Guards b, c, i are code in `reference/safe_construction.py` (`rel_load_checked`, `constraint_or_stop`, `link_unique`)

Status: on main (r14). Card: `agentic-kg-construction/L10-11-deterministic-construction/card.md` (card v3). Not run: Aura, other Neo4j or APOC versions, the lesson's own code, the lesson's own `SimpleKGPipeline` settings and a real LLM (r14: the real library, 1.22.0, was run with a stub LLM and a fake embedder: a second run duplicated Document and Chunk nodes).

## Rules
1. Labels and property keys come from model output: accept only a strict identifier pattern, backtick-quote it, refuse the rest before any query text exists (`reference/safe_construction.py`). Values go in as parameters.
2. A relationship load that MATCHes both ends drops rows with a missing end and says nothing. Per rule, count rows read and distinct id pairs, compare with relationships created, and fail on a difference. Compare against DISTINCT pairs: MERGE collapses repeats, and raw rows would cry wolf.
3. A `LIMIT 1` check proves one row exists, not that all loaded. Use the count compare of rule 2.
4. `CREATE CONSTRAINT ... IF NOT EXISTS` still raises when existing rows break the constraint. The loader must stop on that error; do not swallow it and load anyway.
5. Entity linking by a distance threshold links near names, not same things: `Aurora Pro 2000` vs `Aurora Max 2000` is 0.080 (APOC `jaroWinklerDistance`, lower = closer), under a 0.1 cutoff. Link only when exactly one candidate passes; leave the rest for review. That stops one-to-many links but NOT a single wrong link: with `Aurora Max 2000` as the only candidate for `Aurora Pro 2000` the guard links them (r14 fixture). Anything that matters needs a second distinguishing property that must be equal (`same_prop` in `link_unique`) or a review step. After linking, run the many-to-many check in both directions.
6. State the scale beside every threshold (0-1 or 0-100) and test one boundary pair.
7. Make ingestion re-runnable: MERGE on a content key plus a uniqueness constraint. Report nodes and relationships created per run; the second run should create 0.
8. Strip front matter and fenced code before splitting markdown or picking a title.

## Where the detail lives
Card, with each gotcha's naive and guarded result: `agentic-kg-construction/L10-11-deterministic-construction/card.md`. Code: its `reference/`.
