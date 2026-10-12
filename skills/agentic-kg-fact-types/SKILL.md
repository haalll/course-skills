---
name: agentic-kg-fact-types
description: Use when a model proposes typed statements (subject label, predicate, object label) that a tool must check against an approved list of entity types, and the proposal must be stored reliably; covers batched tool calls losing writes, text-only replies, missing approvals, predicate normalisation and same-turn approval, with ADK 1.5.0 reference code.
---

# Fact types checked against approved entity types (DRAFT; fake models plus 3 live runs)

Status: draft on branch `draft/r10`. Checked against google-adk 1.5.0 with scripted fake models and 3 live Sonnet runs; no SDK mapping.

## Rules
1. Do not trust "one item per call". The real model batched 5 to 7 calls in one response in 3 of 3 runs. ADK keeps only the last call's state writes of a response, so a refused LAST call erases the good ones in that response. Take a list in one call, with a verdict per item and one state write.
2. After every turn read the store, not the model's text. No stored proposal: retry with a corrective message, bounded, then fail closed.
3. Show the model the approved labels (instruction or getter); otherwise it invents labels.
4. Store triples as a list, dedupe exact repeats, normalise predicates. A dict keyed by predicate overwrites.
5. A missing approval or plan is an error that names the missing step. Never `state["x"]` (crash) or an empty default (silent).
6. Approve takes no arguments, refuses an empty store and refuses a proposal made in the same turn.

## Where the detail lives
Card: `agentic-kg-construction/L09-unstructured-schema/card.md`. Code: its `reference/`.
