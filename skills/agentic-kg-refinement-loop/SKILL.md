---
name: agentic-kg-refinement-loop
description: Use when an LLM proposer is checked by an LLM critic in a bounded loop (schema, plan, trade plan) and the loop must fail closed; covers exact-match verdicts, empty verdicts, give-up vs converged, feedback reset and running the loop as a tool, with ADK 1.5.0 reference code.
---

# Proposer/critic loop that fails closed (DRAFT; fake-model tests only)

Status: draft on branch `draft/r9`. Checked against google-adk 1.5.0 with scripted fake models; no live model, no SDK mapping.

## Rules
1. Stop only on an exact verdict (the critic's whole reply is one token). Never `"valid" in text`: it matches "invalid".
2. An empty or missing verdict means "not approved". `output_key` stores nothing at all when the critic's reply has no parts.
3. Bound the loop, and have the checker record `converged` True/False. A loop that hit its bound looks exactly like one that converged unless you record it. A False goes to a human.
4. Reset feedback and counters at the start of a run (`before_agent_callback` on the loop). Otherwise the first `{feedback}` raises KeyError, or a stale verdict from the last run steers the first proposal. `{feedback?}` only fixes the KeyError.
5. Key plan entries by name; refuse a duplicate from another source file, allow a revision from the same file. Do not put two plan-writing calls in one model response (only the last state delta is kept).
6. Running the loop as a tool: state deltas flow back to the coordinator, `escalate` stays inside; the tool result is the last inner event's text, so give the checker a text event.

## Where the detail lives
Card: `agentic-kg-construction/L08-schema-proposal/card.md`. Code: its `reference/`.
