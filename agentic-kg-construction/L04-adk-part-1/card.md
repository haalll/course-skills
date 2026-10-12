---
course: Agentic Knowledge Graph Construction (DeepLearning.AI x Neo4j), lesson 4 of 12
topic: one tool-using agent and its runtime in Google ADK
card_version: 3 (round 6: stop rule corrected after the L05 tests)
status: DRAFT, awaiting review on branch draft/r6 (branched from draft/r3)
pinned_versions: google-adk==1.5.0 (course pin; newer ADK may differ)
verified:
  runtime: false          # nothing was executed; see gotchas below
  static_read: "ADK 1.5.0 wheel source, round 2 (lab/stage1/NOTES.md)"
  sdk_mapping: false      # rests on the first 100,000 of 158,282 chars of the SDK page (I-005)
---

# L04: one agent, one tool, one runtime

## When to use this
- You are building or reviewing an LLM agent that calls a database or other tool.
- You need a rule for when an agent loop should stop, or how to seed session state.
- You want scripted multi-turn conversations as tests.
Not for multi-agent routing (lesson 5).

## Patterns (framework-independent)
Tags: **course** = taught in the lesson; **read** = seen in ADK 1.5.0 source; **inference** = our reasoning.

1. **Uniform tool envelope** [course; house convention, ADK does not require it]. A tool returns
   `{"status": "success", ...}` or `{"status": "error", "error_message": ...}`; the agent's
   instruction says what to do on each branch. Errors become data, not exceptions.
2. **The docstring is the tool contract** [course, ADK-specific]. Name, purpose, args and return
   shape reach the model. Write for the model.
3. **Agent = name + model + description + instruction + tools** [course]. `description` is public
   (drives delegation); `instruction` is private. A `*_v1` name suffix is a convention only.
4. **Parameterised queries, always** [course]. Also whitelist labels, relationship types and property
   names, since query parameters cannot carry those [inference].
5. **Serialise DB results to plain data** before they enter session state [course]. The in-memory
   session service deep-copies sessions on read [read].
6. **The runtime is an event loop** [course]. Read the whole `run_async` stream and take the last final
   event. "Stop on the root's final event" is wrong once the root delegates: the turn's final event is then
   authored by the sub-agent (see gotcha a, L05 card).
7. **Session = (app, user, session id) + state** [course]. The in-memory service copies a state dict passed
   at creation (pydantic validation), so the caller's dict is not aliased in 1.5.0 [run].
8. **Wrap the loop once** [course] and return a structured result (text, tool calls, author), not only
   a string [inference].

## Do / don't
- Do consume the whole stream and keep the last event with `is_final_response()` true (any author). Do not require `author == <root agent name>`: in a delegating team the root never produces the final event (L05 test).
- Do join all text parts of the final event.
- Do pass `state=None` and build a fresh dict per session; never share a default dict.
- Don't `break` on the first final event unless you know no later final event can follow (not shown to occur with LLM transfer in 1.5.0; untested for sequential/parallel agents).
- Don't rely on `parts[0]` alone.

## Gotchas and what is verified
| | Claim | Static read (ADK 1.5.0) | Runtime test | Flag |
|---|---|---|---|---|
| a | Breaking on any final event stops on a sub-agent's reply | `is_final_response()` (events/event.py:95-104) has no author check; it is also true when `skip_summarization` or `long_running_tool_ids` is set | constructed events: naive loop stopped at the sub-agent, author check stopped at root. CORRECTION r6: with real delegation (L05 scenario 1, fake model) the root emits no final event at all, so the author check would return nothing | reproduced; "author check" fix REPLACED by "take the last final event"; course files unread |
| b | `get_session` must be awaited | `async def` at sessions/base_session_service.py:72; the runner awaits it at runners.py:181 and :296 | without `await`: `AttributeError: 'coroutine' object has no attribute 'events'`; with `await`: a Session | reproduced; the course helper's code is unseen |
| c | Mutable `{}` default shared across calls | in-memory service stores `state or {}` (sessions/in_memory_session_service.py:96) | NOT reproduced: with an empty or non-empty shared dict, sessions got separate state objects and writes did not leak | not a gotcha for in-memory 1.5.0; other session services untested; still avoid shared defaults |
| d | Only `parts[0].text` is read | nothing in `is_final_response()` limits parts | constructed two-part final event: `parts[0].text` gave 'Hello ', joined text gave 'Hello world' | reproduced on a constructed event; no live model call |

Runtime tests: google-adk 1.5.0 in a venv, constructed objects, no model call; each run without and with the fix.

## Reference and lab
- `reference/adk-v1.5.0-skeleton.py`: our own skeleton, UNTESTED
- `reference/mapping.md`: ADK to Claude Agent SDK, UNVERIFIED rows marked
- `lab/run-log-template.md`: lab record template
