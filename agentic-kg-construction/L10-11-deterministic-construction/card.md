---
course: Agentic Knowledge Graph Construction (DeepLearning.AI x Neo4j), lessons 10 and 11 of 12
topic: executing the approved plans with code, not agents: (L10) domain graph from CSV via uniqueness constraints + LOAD CSV/MERGE; (L11) lexical + subject graph from markdown via neo4j_graphrag SimpleKGPipeline, then entity resolution to the domain graph
card_version: 2 (desktop draft v1 from the lesson transcripts, plan-side parts checked in the lab, round 12)
status: DRAFT on branch draft/r11; database-bound items NOT run (no database this round)
pinned_versions: google-adk==1.5.0 (course pin); neo4j_graphrag version unknown (not in the narration); rapidfuzz 3.14.6 (our venv)
verified:
  runtime: "Python only, no database, no model: lab/n22/n22_checks.py, out_n22_checks.txt (round 12). Cypher text was built and inspected, never executed"
  static_read: "APOC Strings.java (dev branch) and commons-text JaroWinklerDistance.java read on GitHub in round 12; no Neo4j/APOC release read"
  sdk_mapping: false
  notebook: false         # lesson notebooks not captured; the "naive" code below is OUR reconstruction of what the narration describes
---

# L10-11: deterministic construction after agentic planning

## When to use this
- An LLM (or a person) has produced a plan (node files, relationship files, entity and fact types) and something must now write it to a graph repeatably.
- The mechanical part is the same every run: it should be code with checks, not another agent.

## What the lessons build (own wording, from the narration)
L10, one tool `construct_domain_graph(plan)`: per node rule a uniqueness constraint (label, key column), then `LOAD CSV WITH HEADERS` from the import directory, a per-row subquery that MERGEs the node on the key and sets the listed properties, batched `IN TRANSACTIONS OF 1000 ROWS`; node import only if the constraint step returned no error. Relationship rules: LOAD CSV, MATCH both ends by id, MERGE the relationship. Nodes first, then relationships. The check is a query that finds ONE matching path per relationship rule (LIMIT 1).

L11, tools only: one `SimpleKGPipeline` per markdown file (custom loader that reads markdown, title = first H1 by regex; custom splitter on the `---` page break; schema = approved entity types, relationship types, and patterns built from the approved fact types), giving a lexical graph (chunks, document) and a subject graph (`__Entity__` nodes). Then entity resolution to the domain graph: observed labels, property keys per label, a key normaliser, rapidfuzz key pairing with a threshold, top pair, Jaro-Winkler distance on the values, `MERGE (entity)-[:CORRESPONDS_TO]->(domain)` when distance < 0.1.

## Patterns (framework-independent)
Tags: **course** = taught (transcript only); **run** = reproduced in Python here; **read** = read in source; **inference** = our reasoning.
1. **Agents plan, code executes** [course]. The plan is the boundary: everything in it is untrusted input to the executor (it came from a model).
2. **Idempotent writes**: IF NOT EXISTS constraints, MERGE, ON CREATE / ON MATCH stamps [course].
3. **Constrain, then load; nodes, then relationships; batch large loads** [course].
4. **Verify against the plan by querying the store, with counts** [course, inference]: see gotchas b and d.
5. **Resolve entities on observed labels and keys with an explicit threshold** [course]: see g and h.
6. **Validate identifiers before they reach a query string** [run]: gotcha a.

## Do / don't
- Do accept a label or property key only if it matches a strict identifier pattern, then backtick-quote it; refuse everything else before any query exists (reference/safe_construction.py).
- Do keep approved fact types as a LIST of triples and derive both the relationship-type list and the patterns from it (gotcha e).
- Do strip fenced code and front matter before looking for page breaks and titles (gotcha f).
- Do state the similarity scale next to every threshold (0-1 or 0-100) and test the boundary pair once (gotchas g, h).
- Do report counts: rows read, rows loaded, relationships created, per rule. Not in the lessons; needs a database to run (below).
- Don't treat a `LIMIT 1` path check as "loaded" (gotcha d).
- Don't take "the top pair" blindly when scores tie (gotcha g).

## Gotchas
Result column: **Reproduced** = run here in Python (lab/n22/out_n22_checks.txt); **Read** = source read, nothing run; **Needs database** = not run.

| | Claim | Result (round 12) |
|---|---|---|
| a | String-built Cypher from plan identifiers breaks or injects | **Reproduced (built strings only, never sent to a database).** `My Label` and ``na`me`` give broken constraint text. A label such as `Person {id: row.id}) SET n.admin = true WITH 1 AS x MATCH (m) DETACH DELETE m //` ends up as executable clauses inside the LOAD CSV query text. With the identifier guard all four bad inputs were refused and the good one came out backtick-quoted. Whether Neo4j would run the injected text is not tested; the point is that the plan is model output |
| b | Relationship rows whose from/to id has no node are silently skipped, no count | **Needs database.** Plan-side only: the MATCH-then-MERGE shape returns no row for a missing end, by design of Cypher (not run here). Check: per relationship rule run the same LOAD CSV once with `RETURN count(*)` for rows read, then compare with `count` of that relationship type created by the rule; report both, fail on a difference unless the plan says rows may be dropped |
| c | "Import only if the constraint step had no error": what counts as an error; a constraint that fails on existing duplicates | **Needs database.** Check: (1) make the driver raise on a constraint failure and confirm the tool stops; (2) create a duplicate on the key, run `CREATE CONSTRAINT IF NOT EXISTS` and see whether it raises, returns, or is skipped; (3) confirm no load ran |
| d | A `LIMIT 1` check per rule proves "at least one", not "all rows loaded" | **Needs database.** The logic is plain; the check is a count per rule against the CSV row count (distinct key values for nodes, distinct id pairs for relationships, because MERGE collapses duplicates) |
| e | Schema from a dict keyed by relationship type collapses fact types that share a predicate | **Reproduced.** Three triples with `LIKES` twice gave 2 keys and 2 patterns; the pattern `(Person, LIKES, Beverage)` was lost, 1 of 3. Same cause as L09 gotcha c, reached from the consumer. Whether the lesson's own code does exactly this was not read: it follows the narration ("the keys of the approved fact types") |
| f | `---` splitter and first-H1 title regex mis-handle real markdown | **Reproduced on our reconstruction.** Front matter: naive 3 chunks (metadata becomes a chunk), guarded 2. A `---` inside a fenced block: naive 3, guarded 2. A `# comment` line in a code block before the real title: naive title `install deps`, guarded `Actual Title`. No H1: naive `None`, guarded falls back to the file name |
| g | Key correlation: prefix stripping, threshold scale, tie-breaking | **Reproduced on our reconstruction.** A naive "strip the label prefix" turns `production_date` into `ion_date` and `productid` into `id`; a boundary-aware strip leaves both alone. rapidfuzz `fuzz.ratio` is 0-100: design/description scores 58.8, price/prize 80. A cutoff written 0.9 passed to a 0-100 scorer accepted both pairs; 90 accepted neither. (The demo's 0.5 only pairs design/description if read as 50 on this scale.) Ties: `names` and `nameX` both 88.9 for `name`, so the pair chosen depends on input order |
| h | Jaro-Winkler direction and source | **Read, direction OK for the source read.** APOC `apoc.text.jaroWinklerDistance` returns what `org.apache.commons.text.similarity.JaroWinklerDistance.apply` returns, which is `1 - JaroWinklerSimilarity` (0 identical, 1 unlike), so `< 0.1` means "close" (APOC `dev` branch, commons-text master; other releases and the Aura-bundled APOC were NOT read, and an older library could behave differently). Run in Python with rapidfuzz: `Aurora Pro 2000` vs `Aurora Pro 2001` 0.027, vs `Aurora Max 2000` **0.080**: both link at `< 0.1`, so two product variants differing by one word are merged. Used as a SIMILARITY (the wrong direction) the same test links only `Red`/`Blue`. Availability of APOC on Aura Free is still I-006 (unverified) |
| i | CORRESPONDS_TO can be many-to-many | **Needs database.** Check: `MATCH (e:__Entity__)-[:CORRESPONDS_TO]->(d) WITH e, count(d) AS n WHERE n > 1 RETURN e, n`; and the reverse direction. Also suggested by h: near-identical names link |
| j | Running the pipeline twice duplicates chunks/entities | **Needs database** (and the real pipeline, which also needs an LLM key and embedder). Check: run twice on one file; compare `count(:Chunk)`, `count(:__Entity__)`, `count(:Document)` after each run; then run the correlation twice and compare `count(:CORRESPONDS_TO)` |

## Residual risks, not tested
- Everything that needs a database: b, c, d, i, j and the actual behaviour of the Cypher text. The lesson code, the notebooks and neo4j_graphrag itself were not read.
- Our `split_safe` handles only `---` front matter and triple-backtick fences; tilde fences, indented code and setext headings are not handled.
- A fixed distance threshold (0.1) is a policy choice: h shows it merges variants. Prefer an explicit allow/deny review of linked pairs for anything that matters, or compare more than one property.

## Mapping to the Claude Agent SDK (DEC-001)
Not mapped. The executor is plain code and does not depend on the agent framework; only the hand-over of the approved plan does (see L06 and L08 cards).

## Where it applies
Any "LLM proposes, code executes" pipeline in Hal's systems: the executor validates identifiers, reports dropped rows, and checks counts against the plan, failing closed on a mismatch. See `project-map.md` (not updated this round).
