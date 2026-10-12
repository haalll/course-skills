---
course: Agentic Knowledge Graph Construction (DeepLearning.AI x Neo4j), lessons 10 and 11 of 12
topic: executing the approved plans with code, not agents: (L10) domain graph from CSV via uniqueness constraints + LOAD CSV/MERGE; (L11) lexical + subject graph from markdown via neo4j_graphrag SimpleKGPipeline, then entity resolution to the domain graph
card_version: 3 (desktop draft v1 from the lesson transcripts; plan-side checks round 12, database checks round 13)
status: DRAFT on branch draft/r13; b, c, d, i, j and the local APOC check run on local Neo4j 5.26.14 in round 13 (j on a stand-in, not SimpleKGPipeline)
pinned_versions: google-adk==1.5.0 (course pin); neo4j_graphrag version unknown (not in the narration); rapidfuzz 3.14.6 (our venv)
verified:
  runtime: "Round 12: Python only (lab/n22/n22_checks.py, out_n22_checks.txt). Round 13: local Neo4j 5.26.14 Community, JDK 17, bundled APOC 5.26.14, localhost only, fake embedder, tiny data (lab/n23/n23_db_checks.py, out_n23_db_checks.txt, out_n23_memory.txt)"
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
- Do report counts: rows read, rows loaded, relationships created, per rule, and compare against DISTINCT keys (gotchas b, d; run on a database in round 13). Not in the lessons.
- Don't link an entity by a distance threshold alone when more than one candidate passes: leave it for review (gotchas h, i).
- Don't treat a `LIMIT 1` path check as "loaded" (gotcha d).
- Don't take "the top pair" blindly when scores tie (gotcha g).

## Gotchas
Result column: **Reproduced** = run here (Python only: lab/n22/out_n22_checks.txt; with a database: lab/n23/out_n23_db_checks.txt); **Read** = source read, nothing run.

| | Claim | Result (rounds 12-13) |
|---|---|---|
| a | String-built Cypher from plan identifiers breaks or injects | **Reproduced (built strings only, never sent to a database).** `My Label` and ``na`me`` give broken constraint text. A label such as `Person {id: row.id}) SET n.admin = true WITH 1 AS x MATCH (m) DETACH DELETE m //` ends up as executable clauses inside the LOAD CSV query text. With the identifier guard all four bad inputs were refused and the good one came out backtick-quoted. Whether Neo4j would run the injected text is not tested; the point is that the plan is model output |
| b | Relationship rows whose from/to id has no node are silently skipped, no count | **Reproduced (round 13, local Neo4j 5.26.14, lab/n23/out_n23_db_checks.txt).** Six CSV rows, two with an end id that has no node, one exact duplicate pair: the MATCH-then-MERGE load returned no error and created 3 relationships. Naive = no compare. Guard: per rule, read the row count and the count of distinct id pairs, then compare with relationships created; it fired (`5 distinct pairs in file, 3 created`). Control: a clean file (4 rows, one duplicate pair, so 3 distinct) created 3 and passed, so duplicates collapsed by MERGE are not a false alarm if you compare against DISTINCT pairs, not raw rows |
| c | "Import only if the constraint step had no error": what counts as an error; a constraint that fails on existing duplicates | **Reproduced (round 13).** With two nodes sharing the key, `CREATE CONSTRAINT ... IF NOT EXISTS` RAISED `ConstraintCreationFailed` (IF NOT EXISTS does not skip it) and no constraint existed afterwards. A flow that swallows the error and loads anyway still loaded (2 nodes created, constraint missing); a flow that stops on the error loaded nothing. Whether the lesson's code swallows the error was not read |
| d | A `LIMIT 1` check per rule proves "at least one", not "all rows loaded" | **Reproduced (round 13).** On the dropped-rows load of b the `LIMIT 1` check found a relationship ("loaded") while 3 of 5 distinct pairs existed; the count check against distinct pairs failed. Compare against distinct key values for nodes and distinct id pairs for relationships, because MERGE collapses duplicates |
| e | Schema from a dict keyed by relationship type collapses fact types that share a predicate | **Reproduced.** Three triples with `LIKES` twice gave 2 keys and 2 patterns; the pattern `(Person, LIKES, Beverage)` was lost, 1 of 3. Same cause as L09 gotcha c, reached from the consumer. Whether the lesson's own code does exactly this was not read: it follows the narration ("the keys of the approved fact types") |
| f | `---` splitter and first-H1 title regex mis-handle real markdown | **Reproduced on our reconstruction.** Front matter: naive 3 chunks (metadata becomes a chunk), guarded 2. A `---` inside a fenced block: naive 3, guarded 2. A `# comment` line in a code block before the real title: naive title `install deps`, guarded `Actual Title`. No H1: naive `None`, guarded falls back to the file name |
| g | Key correlation: prefix stripping, threshold scale, tie-breaking | **Reproduced on our reconstruction (the lesson narration says it flips the score into a similarity before comparing with 0.9, so the scale trap may not apply to its code; this is a general rule, not a lesson defect).** A naive "strip the label prefix" turns `production_date` into `ion_date` and `productid` into `id`; a boundary-aware strip leaves both alone. rapidfuzz `fuzz.ratio` is 0-100: design/description scores 58.8, price/prize 80. A cutoff written 0.9 passed to a 0-100 scorer accepted both pairs; 90 accepted neither. (The demo's 0.5 only pairs design/description if read as 50 on this scale.) Ties: `names` and `nameX` both 88.9 for `name`, so the pair chosen depends on input order |
| h | Jaro-Winkler direction and source | **MOST USEFUL LINE FOR PRODUCT/ENTITY NAMES. Reproduced on the bundled APOC (round 13, local 5.26.14): `apoc.text.jaroWinklerDistance('Aurora Pro 2000','Aurora Max 2000')` = 0.080, `Pro 2000` vs `Pro 2001` = 0.027, `Red`/`Blue` = 1.0, identical = 0.0, so `< 0.1` is the right direction AND merges two different products (see i). Source read (earlier round):** APOC `apoc.text.jaroWinklerDistance` returns what `org.apache.commons.text.similarity.JaroWinklerDistance.apply` returns, which is `1 - JaroWinklerSimilarity` (0 identical, 1 unlike), so `< 0.1` means "close" (APOC `dev` branch, commons-text master; other releases and the Aura-bundled APOC were NOT read, and an older library could behave differently). Run in Python with rapidfuzz: `Aurora Pro 2000` vs `Aurora Pro 2001` 0.027, vs `Aurora Max 2000` **0.080**: both link at `< 0.1`, so two product variants differing by one word are merged. Used as a SIMILARITY (the wrong direction) the same test links only `Red`/`Blue`. Availability of APOC on Aura Free is still I-006 (unverified; the local result says nothing about Aura) |
| i | CORRESPONDS_TO can be many-to-many | **Reproduced (round 13), using the bundled APOC distance < 0.1.** Entities `Aurora Pro 2000` and `Aurora Max 2000` against products `Aurora Pro 2000`, `Aurora Max 2000`, `Aurora Pro 2001`, `Zephyr Basic`: the naive link created 6 relationships, `Aurora Pro 2000` pointing at 3 products and `Aurora Max 2000` at 2; the check `MATCH (e:__Entity__)-[:CORRESPONDS_TO]->(p) WITH e, count(p) AS n WHERE n > 1` returned both, and the reverse check returned 2 products. Guard: link only when exactly one candidate is under the threshold; it created 1 link (`Zephyr Basic`), left the two Aurora entities unlinked for review, and both checks came back empty |
| j | Running the pipeline twice duplicates chunks/entities | **Reproduced on a stand-in (round 13), NOT on the real pipeline.** Our own ingest with a FAKE local embedder (sha256-derived 8-number vector; no provider key): the CREATE-per-chunk version went from 3 to 6 Chunk nodes and 3 to 6 FROM_DOCUMENT on the second run; the MERGE-on-content-key version with a uniqueness constraint created 0 nodes and 0 relationships on the second run, and a raw duplicate CREATE was rejected by the constraint. Whether `SimpleKGPipeline` itself duplicates was not run (needs the library, a real LLM key and the lesson's code) |

## Residual risks, not tested
- Database checks ran on local Neo4j 5.26.14 Community with its bundled APOC, tiny hand-made data (3-6 rows). Not tested: Aura, other Neo4j/APOC versions, the lesson's own Cypher, `SimpleKGPipeline` (j used our own ingest and a fake embedder). The lesson code, the notebooks and neo4j_graphrag itself were not read.
- Our `split_safe` handles only `---` front matter and triple-backtick fences; tilde fences, indented code and setext headings are not handled.
- A fixed distance threshold (0.1) is a policy choice: h shows it merges variants. Prefer an explicit allow/deny review of linked pairs for anything that matters, or compare more than one property.

## Mapping to the Claude Agent SDK (DEC-001)
Not mapped. The executor is plain code and does not depend on the agent framework; only the hand-over of the approved plan does (see L06 and L08 cards).

## Where it applies
Any "LLM proposes, code executes" pipeline in Hal's systems: the executor validates identifiers, reports dropped rows, and checks counts against the plan, failing closed on a mismatch. See `project-map.md` (not updated this round).
