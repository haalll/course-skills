---
name: agentic-kg-approval-gate
description: Use when an agent must get the user's confirmation of a goal, plan or schema before acting, built from a "set perceived" tool and an argument-free "approve" tool in Google ADK; covers the same-turn hole, lost state writes from parallel tool calls, and reading the approved value in downstream instructions.
---

# Approval gate from two tools (DRAFT; scripted-fake-model tests only, no live model)

Status: draft on branch `draft/r7`. Checked against google-adk 1.5.0; a real model was not used.

## Rules
1. Two tools: one writes the perceived value under one state key; the other takes NO arguments, errors if the
   perceived key is missing, and only copies perceived to approved.
2. Put the check in the tool; the prompt alone is not a gate. Write the error text for the model: what failed, what to do.
3. Refuse approval in the invocation that wrote the perceived value (compare `tool_context.invocation_id`),
   or a model can set and approve in one turn. This guarantees a turn boundary, not consent.
4. Never rely on one model response carrying both calls: parallel function responses keep only the last `state_delta`.
5. Downstream agents read the value with `{approved_user_goal}` in the instruction (fails loudly if absent)
   or `{approved_user_goal?}` (renders empty).
6. For a real human gate, put the confirmation in the client, outside the model.

## Where the detail lives
Card: `agentic-kg-construction/L06-user-intent/card.md`. Code: its `reference/`. SDK mapping there is unverified.
