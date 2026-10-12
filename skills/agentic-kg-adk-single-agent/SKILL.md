---
name: agentic-kg-adk-single-agent
description: Use when building or reviewing an LLM agent that calls a database or tool, especially Google ADK or Claude Agent SDK agents. Covers the tool return envelope (status/error_message), parameterised queries, event-loop stop conditions, session state seeding, and scripted multi-turn tests. Not for multi-agent routing.
---

# Single agent with one tool (DRAFT, not runtime-verified)

Status: draft on branch `draft/r6` (from `draft/r3`). Gotchas below were read in ADK 1.5.0 source, not executed.

## Rules
1. Tools return `{"status": "success", ...}` or `{"status": "error", "error_message": ...}`; say in the
   agent instruction what to do on each branch.
2. Pass values as query parameters. Whitelist labels, relationship types and property names.
3. Convert DB results to plain dicts and strings before they enter session state.
4. Consume the whole event stream and keep the last final event (any author). Do not wait for a final event authored by the root: once the root delegates it never produces one.
5. Join all text parts of the final event; do not read only the first part.
6. Seed session state with `None` and a fresh dict per session; never a shared default.
7. Wrap the loop once and return a structured result so conversations can be scripted as tests.

## Where the detail lives
Card: `agentic-kg-construction/L04-adk-part-1/card.md`. Code: its `reference/` directory.
The Claude Agent SDK mapping there is unverified; confirm against current docs first.
