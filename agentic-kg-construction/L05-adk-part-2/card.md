---
course: Agentic Knowledge Graph Construction (DeepLearning.AI x Neo4j), lesson 5 of 12
topic: a team of agents (root + sub-agents), delegation, and shared session state in Google ADK
card_version: 2 (desktop draft v1 from the transcript, checked and corrected in the lab, round 6)
status: DRAFT, awaiting review on branch draft/r6
pinned_versions: google-adk==1.5.0 (course pin; newer ADK may differ)
verified:
  runtime: "scripted fake models only, no live model call (lab/stage1/tests/l05_team.py, round 6)"
  static_read: "ADK 1.5.0 source, locators in the table below, re-read round 6"
  sdk_mapping: false      # not looked at in round 6
---

# L05: a root agent, two sub-agents, and shared state

## When to use this
- One request type should be routed to a specialist agent rather than handled by a generalist.
- Several agents or tools must share facts gathered earlier in a session (a user's name, an approved goal).
- You need to debug who did what in a multi-agent turn.
Builds on L04 (single agent, event loop). Note: this lesson corrects L04's stop rule (gotcha a).

## Patterns (framework-independent)
Tags: **course** = taught in the lesson; **read** = seen in ADK 1.5.0 source; **run** = reproduced with a
scripted fake model (no real model); **inference** = our reasoning.

1. **Root/coordinator + specialists** [course]. The root has no tools of its own; it answers or delegates.
   Each specialist owns one capability and its tool(s).
2. **Delegation is driven by text** [course, read]. ADK itself appends to every agent that can transfer a
   list of the possible targets with their names and `description`s, plus the instruction to call the
   transfer function when another agent fits better. So the `description`s do most of the routing; the root's
   own `instruction` only adds emphasis. Most tuning time goes into these strings.
3. **Delegation is a function call that hands over the turn** [run]. Event order in one turn:
   (1) delegator event, function call `transfer_to_agent(agent_name=...)`, not final;
   (2) delegator event, the function response, with `actions.transfer_to_agent` set, not final;
   (3) events authored by the sub-agent, ending in its final response.
   The sub-agent runs inside the delegator's own event stream [read].
4. **Control stays with the last agent, by default** [run, read]. The next user message goes to the agent
   that spoke last, provided it and every ancestor are LLM agents that may transfer to their parent.
   Otherwise the turn starts at the root. If the last event is an unanswered function call, its author gets
   the answer. Make an agent a one-shot specialist with `disallow_transfer_to_parent=True`.
5. **Sub-agents may hand off to peers directly** [run]. Default flags allow sibling transfers, so routing is
   not always "back through root". Restrict with `disallow_transfer_to_peers`.
6. **Few-shot hints inside instructions** [course]. Listing example phrasings ("bye", "see you") makes
   routing more reliable; cheap insurance.
7. **Session state is a shared dict written through deltas** [course, run]. A tool writes
   `tool_context.state[key]`; that shows up as `actions.state_delta` on the tool's function-response event
   and the session service applies it. Keys starting with `temp:` are skipped when applying [read].
8. **Two ways to write state** [run]: (a) a tool with a parameter named `tool_context`; (b) an agent's
   `output_key`, which saves that agent's final response text (all text parts joined) under the key.
9. **Read state with a default** [course]: `state.get(key, default)`, so a tool degrades when an earlier step never ran.
10. **Verbose traces as the debugging view** [course, run]: print author, calls, function responses, final flag,
    transfer target and state_delta for every event before trusting a summary.

## Do / don't
- Do write sub-agent `description`s for other agents to read: what it handles and what it does not.
- Do give the root no tools when its only job is routing.
- Do read shared state with a default.
- Do consume the whole `run_async` stream and take the last final event (gotcha a).
- Do name the injected parameter exactly `tool_context`; annotate it `ToolContext` for readers.
- Don't assume the next turn starts at the root (pattern 4); set `disallow_transfer_to_parent` when it must.
- Don't put `output_key` on an agent that delegates, unless you want the delegate's answer stored there (gotcha e).
- Don't let a stateful tool trust an unconfirmed value: the lesson's trace shows the model inventing a name from
  an ambiguous message and writing it to state before the user corrected it [course]. Our fake-model test
  cannot show this; it is a design lesson.

## Gotchas and what is verified
| | Claim | Static read (ADK 1.5.0) | Runtime test (scripted fake model) | Flag |
|---|---|---|---|---|
| a | In a team, "stop on the root's final event" never fires when a sub-agent answers | `is_final_response()` has no author check (events/event.py:95-104) | scenario 1: the only final event of the turn is authored by the sub-agent; the root's events are non-final. So the L04 rule would return nothing | reproduced; replaces L04's rule |
| b | Control stays with the last sub-agent across turns | `_find_agent_to_run` (runners.py:335-376), `_is_transferable_across_agent_tree` (:378-398) | scenario 1: turn 2 authored by the sub-agent although the root script was empty; scenario 2 (`disallow_transfer_to_parent=True`): turn 2 authored by root | reproduced |
| c | A tool gets `tool_context` only if it is the last parameter and typed `ToolContext` (DRAFT CLAIM, WRONG) | injection tests the parameter NAME: `'tool_context' in signature.parameters` (tools/function_tool.py:82, :131); the name is also hidden from the model schema (:60) | position first or last: injected; untyped `tool_context`: injected; a `ToolContext`-typed parameter with another name: declaration build raises `ValueError` ("Failed to parse the parameter ctx") | reproduced; draft corrected. Failure is loud, not silent |
| d | The model may write a guessed value to state | none (design lesson) | not testable with a fake model | course observation, not a framework bug |
| e | `output_key` of a delegating agent captures its delegate's final answer | the agent's flow yields the sub-agent's events (flows/llm_flows/base_llm_flow.py:475-481) and `_run_async_impl` applies `output_key` to every event it yields (agents/llm_agent.py:275-276, :432-447), with no author check | scenario 3: only the greeter had `output_key`; after it handed off to a peer, state held the peer's text under the greeter's key | reproduced |

Not covered: a real model's behaviour (does it follow the transfer instruction, emit several parts), other session
services, `run_live`, parallel/sequential/loop agents.

## Reference and lab
- `reference/mapping.md`: ADK to Claude Agent SDK, UNVERIFIED
- test script: lab/stage1/tests/l05_team.py in the course-lab repo (not in this repo)
