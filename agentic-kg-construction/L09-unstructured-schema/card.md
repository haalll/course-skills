---
course: Agentic Knowledge Graph Construction (DeepLearning.AI x Neo4j), lesson 9 of 12
topic: schema proposal for unstructured data: an entity-type agent, then a fact-type agent whose tool checks each triple against the approved entity types
card_version: 2 (desktop draft v1 from the lesson transcript, checked and corrected in the lab, round 11)
status: DRAFT, awaiting review on branch draft/r10
pinned_versions: google-adk==1.5.0 (course pin; newer ADK may differ)
verified:
  runtime: "scripted fake models (lab/stage1/tests/l09_facts.py, l09_lastcall.py, l09_reference_check.py) plus 3 live runs of the fact agent with claude-sonnet-5-5 through ADK (lab/stage1/live/live_r11.py, round 11)"
  static_read: "function-response merge (functions.py:504-508), mandatory-argument refusal (function_tool.py:91-99), invocation_id (readonly_context.py:42) read in the 1.5.0 wheel"
  sdk_mapping: false      # see reference/mapping.md
  notebook: false         # lesson code and notebook not captured; the "naive" tools are OUR reconstruction of what the narration describes
---

# L09: entity types first, then fact types checked against them

## When to use this
- Free text has to become typed statements ("person likes beverage") and you want the allowed types fixed before any statement is stored.
- A model proposes a schema in several steps and each step needs a corrective error when it breaks the previous step's output.

## What the lesson builds (own wording, from the narration)
- Input: markdown product reviews. The earlier steps are simulated by seeding state: approved goal, approved files, and the L08 plan (nodes only).
- Agent 1 proposes a LIST of entity types: "well-known" ones are the node labels already in the plan (read through a getter), "discovered" ones recur in the text and serve the goal. Tools: set proposed (whole list), get proposed, approve (no arguments, copies proposed to approved), get approved, get well-known.
- Agent 2 proposes fact TYPES as triples (subject label, predicate, object label), one triple per tool call. The tool reads the approved entity types and returns an error if either label is not among them, otherwise stores the triple. Then get proposed, approve (copy).
- The narrated run failed once: the fact agent wrote its proposal as prose and never called the tool; the presenter re-ran it.

## Patterns (framework-independent)
Tags: **course** = taught in the lesson (transcript only); **run** = reproduced with scripted fake models; **live** = seen with a real model (n=3); **inference** = our reasoning.

1. **Split "kinds of things" from "what is said about them"** [course]: approve the entity types first, and make the fact tool enforce them.
2. **Anchor new extraction to the existing schema** [course]: well-known labels come from the structured plan so text and table data land on the same labels.
3. **One item per call when each needs a corrective error** [course]: but the model may not keep to it (gotcha b, live).
4. **Ask for types, not extractions** [course]: the extraction runs later.
5. **Check state after the turn** [course, run]: "proposal shown in chat" is not "proposal stored"; a guard looks at the store, retries with a corrective message, then fails closed (gotcha a).
6. **Tell the agent which labels exist** [live]: given no list, the real model guessed `User`, `Reviewer`, `Customer`, `Rating`, `City` and the tool refused them (run l09-1). Put the approved list in the instruction or a getter result.

## Do / don't
- Do store facts as a list of triples, drop exact duplicates, and normalise the predicate to one spelling.
- Do make the fact tool fail with a message that names the missing step when no approved entity types exist.
- Do accept a LIST of facts in one call, with a verdict per item, one state write for the whole call; the real model batched in 3 of 3 runs.
- Do check the store after every turn; fail closed (caller must not approve) after a bounded number of retries.
- Do refuse approval in the turn that wrote the proposal, and when nothing is stored (L06 pattern).
- Do make "not found" errors name the near match ("Did you mean 'Person'?") and the approved list.
- Don't rely on "one triple per call" in the prompt, and don't let the tool's success message stand in for storage.
- Don't read plan or approval state with `state["key"]`: a missing key crashes the turn; an empty default hides the problem.

## Gotchas
| | Claim | Result (google-adk 1.5.0, round 11; out_l09.txt, out_l09_lastcall.txt, live/out_l09-*.txt) |
|---|---|---|
| a | A text-only proposal stores nothing and a later approve approves nothing | **Reproduced (fake)**: prose turn has 0 tool calls and no `proposed_facts`. Approve with nothing stored: lesson-style `.get(..., [])` returns success with `approved_facts=[]`; the `state[...]` form raises `KeyError` and ends the turn; the checked approve returns an error. Guard: stored after 1 retry when the model recovers, FAILED CLOSED after 2 retries when it never calls the tool. **Not seen live**: the real model called the tool in 3 of 3 runs |
| b | Several `add_proposed_fact` calls in one response lose most triples | **Draft hypothesis NOT reproduced as stated.** With a list store, 3 calls in one response stored 3: each call rewrites the list it reads from the in-turn view (T-020). **Reproduced in a narrower form**: ADK keeps only the LAST function-response's actions (functions.py:504-508), so if the last call is refused (tool error, or a missing mandatory argument, function_tool.py:91-99) the whole response's writes are lost: 2 good + refused last = 0 stored, all reported success; refused first = 2 stored. **Live**: the real model batched in 3 of 3 runs (5, 7 and 7 calls in one response) despite "one triple per call". Run l09-1 (agent not told the labels): 1 success among 5 refusals, last call refused, final state `{}`, yet the model's text said it recorded one fact type. Runs l09-2/l09-3: last call missed an argument; the 6 good calls survived only because the model's retry in the next response rewrote the whole list (fake: 2 good + missing last + retry = 3 stored). A list-taking tool with per-item verdicts stored 3 of 4 with the bad one named |
| c | Keying triples by predicate overwrites | **Reproduced**: `(Person LIKES Beverage)` then `(Person LIKES Product)`: dict by predicate stored 1, list stored 2, an exact duplicate stored once |
| d | Missing approved entity types: unclear failure | **Reproduced**: `state["approved_entities"]` raises KeyError; `.get(..., [])` refuses every triple with "Label Person doesn't exist", which blames the label; the checked tool says no approved types are in state |
| e | Exact label match, free-text predicate, near-duplicate discovered types | **Reproduced**: `person` refused (good); the lesson-style message gives no hint, the checked one says "Did you mean 'Person'?" and lists the approved types. Predicates `HAS_ISSUE`, `has_issue`, `Has Issue` stored as 3 facts, normalised stored 1. A discovered `Products` beside well-known `Product` was accepted, the checked set tool refused it. **Not reproduced**: the retry loop the draft feared (a scripted model cannot show it; live, the refused labels were different invented ones, not the same one repeated) |
| f | Empty or missing plan gives silent empty well-known types | **Reproduced**: plan missing or without nodes: `state[...]` raises KeyError, `.get` returns success with `types: []`, checked getter returns an error naming the missing step |
| g | Approve copies proposed to approved with no check the user saw it | **Reproduced**: add and approve in one response: both succeed, `approved_facts` holds the triple, `proposed_facts` is gone (last delta wins). Checked approve refuses a same-turn proposal; the proposal is lost too in that case (`approved_facts=None`), so the user must start over. Propose in one turn, approve in the next: works |

Also seen: 4 OpenTelemetry "Failed to detach context" messages in err_l09.txt (cause not investigated; results unaffected).

## Residual risks, not tested
- Real model: 3 runs, one prompt family, synthetic reviews written by us; no prose-only turn was seen, so the guard's retry message was only tested on scripted models.
- A batch tool trades the lesson's per-fact correction round trips for per-item verdicts; whether the real model reads the verdicts and fixes the bad items was not run.
- Entity-agent side (set/approve of the type list, discovered vs well-known choice by a real model) not run live.
- Lesson code and notebook were not read; the lesson's own tool signatures are unknown.

## Mapping to the Claude Agent SDK (DEC-001)
Unverified. See `reference/mapping.md`.

## Where it applies
See `project-map.md`.
