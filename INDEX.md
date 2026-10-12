# Index: which card and Skill to load for which job

Course: Agentic Knowledge Graph Construction (DeepLearning.AI x Neo4j). Cards and code are in our own wording (DEC-002). Every card is a DRAFT checked in a lab on a small scale; "open limits" says what was NOT checked. Read the card's gotcha table before relying on a rule: each row says whether it was reproduced, and with what.

Pinned: google-adk 1.5.0 (the course's reference framework; the target framework for our agents is the Claude Agent SDK, so every ADK mapping below is a pattern to re-check, not code to copy). Database checks: local Neo4j 5.26.14 Community, tiny data.

| Lesson | Card (`agentic-kg-construction/…/card.md`) | Skill (`skills/…/SKILL.md`) | Use when | Open limits |
|---|---|---|---|---|
| L04 | `L04-adk-part-1` | `agentic-kg-adk-single-agent` | A model-driven agent calls a database or tool: return envelope, parameterised queries, stop on the agent's own final event, scripted multi-turn tests | ADK source read and scripted models only; Claude Agent SDK mapping not verified; the card's reference skeleton was not run with a live model |
| L05 | `L05-adk-part-2` | `agentic-kg-adk-multi-agent` | A router plus specialist agents sharing facts through session state | Scripted fake models only; no live team run; SDK mapping unverified |
| L06 | `L06-user-intent` | `agentic-kg-approval-gate` | Something must be confirmed by the user before an agent acts (perceived plan, then argument-free approve) | Fake models; the SDK permission hook and callback fired in small live smokes (n=1 to 2), not a full gate port |
| L07 | `L07-file-suggestions` | `agentic-kg-confined-file-tools` | An agent reads local files through tools you write: confine paths to one root, check suggestions against a listing, cap bytes | Throwaway files and fake models; SDK Read-rule smokes n=1 each; a literal `..` path resolving outside was not tested (the harness stopped it first); listing filter not run live |
| L08 | `L08-schema-proposal` | `agentic-kg-refinement-loop` | A proposer is checked by a critic in a bounded loop and must fail closed (exact verdict, stored plan, give-up vs converged) | Fake models plus a handful of live runs. Checker now also requires every caller-expected file to be planned (v4) and fails a plan citing files outside that set (v5); fake-model before/after; the earlier live hole was a converged run with one of two files unplanned). The checker's text event is shown to reach the proposer's next request (scripted replay); how a real model reacts is not measured |
| L09 | `L09-unstructured-schema` | `agentic-kg-fact-types` | A model proposes typed statements through a tool that checks them against an approved type list; batched calls must not lose writes | Fake models and 3 live runs; ADK-specific merge rule for parallel calls (SDK behaviour not checked) |
| L10-11 | `L10-11-deterministic-construction` | `agentic-kg-safe-construction` | Code turns an approved plan into database writes: identifier guard, silent row drops, constraint step, similarity linking, re-runnable ingestion | Local Neo4j only (not Aura); tiny data; APOC availability on Aura unchecked; real `SimpleKGPipeline` run once with a stub LLM and fake embedder, not with the lesson's settings or a real model. A distance threshold links near names, and even one candidate can be wrong: require an equal second property or a review step |
| L01-03, L12 | none | none | Conceptual lessons and the closing quiz; no card was written | — |

Where a card might apply to our own systems: `project-map.md` (candidate uses only, none tried).

Order of use for a new job that builds a graph from model-written plans: L06 gate → L07 file tools → L08 critic loop → L09 fact types → L10-11 construction, each fail-closed: nothing downstream acts on a plan whose loop gave up.

Reference code sits in each card's `reference/`. Code that touches a database takes a `run(cypher, **params)` callable, so it can be pointed at any driver.
