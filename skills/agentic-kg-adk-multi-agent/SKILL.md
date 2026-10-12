---
name: agentic-kg-adk-multi-agent
description: Use when building or debugging a multi-agent team in Google ADK (root agent plus sub-agents): delegation by description, which agent gets the next turn, tool_context and output_key state writes, and how to read the event stream. Not for single-agent loops.
---

# ADK agent team (DRAFT; scripted-fake-model tests only, no live model)

Status: draft on branch `draft/r6`. Checked against google-adk 1.5.0; a real model was not used.

## Rules
1. Delegation is routed by each sub-agent's `description`; ADK adds the target list to the prompt itself.
2. A delegating turn has three parts: transfer call, function response with the target, then the sub-agent's events.
3. The turn's final event usually belongs to a sub-agent: read the whole stream and take the last final event;
   never wait for a final event authored by the root.
4. The next turn goes to the last speaker unless it or an ancestor has `disallow_transfer_to_parent=True`.
5. Tools get the context only through a parameter named exactly `tool_context`.
6. State writes arrive as `state_delta` on events; `output_key` stores an agent's final text, including a
   delegate's if the agent handed off; so avoid `output_key` on delegators.
7. Read state with `.get(key, default)`; do not trust a value the model inferred from an ambiguous message.

## Where the detail lives
Card: `agentic-kg-construction/L05-adk-part-2/card.md`. SDK mapping there is unverified.
