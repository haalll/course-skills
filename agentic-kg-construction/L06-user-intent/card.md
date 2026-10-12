---
course: Agentic Knowledge Graph Construction (DeepLearning.AI x Neo4j), lesson 6 of 12
topic: user-intent agent: agree a goal with the user through a perceive -> approve pair of tools
card_version: 2 (desktop draft v1 from the lesson transcript, checked and corrected in the lab, round 7)
status: DRAFT, awaiting review on branch draft/r7
pinned_versions: google-adk==1.5.0 (course pin; newer ADK may differ)
verified:
  runtime: "scripted fake models only, no live model call (lab/stage1/tests/l06_gate.py, round 7)"
  static_read: "ADK 1.5.0 source, locators in the table below, read round 7"
  sdk_mapping: false      # not looked at in round 7 (I-005)
  notebook: false         # lesson notebook not captured; prompt wording and the goal-size check are course claims only
---

# L06: an approval gate built from two tools

## When to use this
- An agent must not act on its own reading of what the user wants until the user has confirmed it.
- Downstream agents need one agreed, structured goal in shared state to steer by.
- Any human-in-the-loop checkpoint: approve a plan, a file list, a schema, an order.
Builds on L05 (shared state through `tool_context`, delegation by description).

## Patterns (framework-independent)
Tags: **course** = taught in the lesson (transcript only); **read** = seen in ADK 1.5.0 source; **run** = reproduced
with a scripted fake model (no real model); **inference** = our reasoning.

1. **Split "I think you mean" from "you approved"** [course, run]. Tool 1 (`set_perceived_user_goal`) writes the
   agent's current understanding to state under one key. Tool 2 (`approve_perceived_user_goal`) takes no
   arguments and only copies that value to a second key. The approved value can then only be something that was
   first written as perceived. Run: the approval tool's model-facing schema has no parameters (scenario 7).
2. **The gate lives in the tool, not only in the prompt** [course, run]. Tool 2 checks that the perceived key
   exists and returns an error otherwise; state stays unchanged (scenario 2).
3. **Error messages written for the model** [course, run]. The error says what went wrong and what to do next
   ("set the perceived goal first, or ask the user clarifying questions"). It reaches the model as the function
   response with `status: error` (scenario 2). Same envelope as L04.
4. **A goal is a small fixed structure** [course]: `kind_of_graph` (at most three words) + `graph_description`
   (a few sentences). The lesson repeats the definition in the instruction, the tool docstrings and the arguments.
   The size limit is prompt-level only; add a check in the tool if it must hold.
5. **Prompt assembled from named parts** [course]: role and goal; conversational hints (domain examples the model
   may not know); output definition; step-by-step directions. Each part a separate string, joined.
6. **Repeat the contract wherever the model looks** [course]: instruction, docstring, argument names, error text.
7. **The description serves the coordinator** [course]: it states the agent's role in the wider workflow so the
   coordinator delegates at the right step (L05 pattern 2).
8. **Scripted conversations must branch** [course, inference]. A real model may ask a clarifying question before it
   sets the goal; a script for a real model should check state and adapt. (Our fake-model scripts are fixed, so this
   was not exercised.)
9. **A turn boundary between "set" and "approve"** [run]. Store `tool_context.invocation_id` next to the perceived
   value and have the approval tool refuse while the current invocation id is the same. Refused in the same turn,
   accepted in the next (scenarios 5, 6). This enforces "the user had a turn to see it", not "the user agreed".
10. **Downstream agents read the approved goal by instruction templating** [read, run]. `{approved_user_goal}` in an
    instruction is filled from session state; a dict is rendered with `str()`. A missing key raises `KeyError` when
    that agent runs, so the agent fails loudly before approval; `{approved_user_goal?}` renders empty instead
    (scenario 8).

## Do / don't
- Do make the approval tool argument-free, so it cannot approve something the user never saw.
- Do check preconditions inside the tool and return a corrective error.
- Do keep the goal schema tiny and fixed.
- Do add the invocation-id check (pattern 9) if a same-turn approval would be harmful.
- Do give downstream agents `{key}` (fail loud) or `{key?}` (degrade) on purpose.
- Don't trust the prompt alone to enforce an approval step.
- Don't let two state-writing tools be called in one model response when order or both writes matter (gotcha d).
- Don't write a test script for a real model that assumes it never asks a question first.

## Gotchas and what is verified
| | Claim | Static read (ADK 1.5.0) | Runtime test (scripted fake model) | Flag |
|---|---|---|---|---|
| a | The approval tool can run in the same turn that (re)sets the goal, before the user saw the new value (course trace: on "I approve" the model set again, then approved) | nothing in the tool path checks it; `invocation_id` is available on the tool context (agents/readonly_context.py:42-44) and is new per `run_async` call (runners.py:419) | scenario 3: set then approve in one turn, both succeed, `approved_user_goal` stored. Scenarios 5, 6: with the invocation-id check the same-turn attempt is refused and the two-turn path works | reproduced; mitigation works for "same turn", not for "user agreed" |
| b | "ToolContext is injected when it is the last argument" (course narration) | injection tests the parameter NAME (tools/function_tool.py:82, :131) | not re-run here; result from L05 (position first/last and untyped all inject) | course error; see L05 gotcha c |
| c | Approval depends on the model reading the user's words; nothing checks the user said yes | none found | not testable with a fake model | design limit [inference]. A hard gate is outside the model: a human-confirmation step in the client or an SDK permission hook |
| d | Two tools called in ONE model response overwrite each other's state writes (NEW) | when parallel function responses are merged, each event's actions are copied over the previous ones, so only the last `state_delta` survives (flows/llm_flows/functions.py:502-509) | scenario 4: [set, approve] in one response: both report success, stored state has `approved_user_goal` but no `perceived_user_goal`. Scenario 5b (hardened pair): approval refused, and the `set` write is lost too (state empty) | reproduced. Consequence: a state-writing pair must not rely on one response carrying both calls |
| e | `{key}` in an instruction raises if the key is missing; `{key?}` is optional (NEW) | utils/instructions_utils.py:79-81, :100-104; called from flows/llm_flows/instructions.py:76 | scenario 8: present key, `{key}` and `{key?}` render the dict; absent key: `KeyError: Context variable not found` vs empty string | reproduced |

Not covered: a real model's behaviour (does it call approve early, does it ask clarifying questions, does it follow
the docstrings), the lesson notebook's actual prompts, other session services, `run_live`, whether parallel
calls occur with a real model (the lesson trace shows sequential calls in one turn).

## Reference and lab
- `reference/approval_gate_adk_1.5.0.py`: the two tool pairs we tested, our own wording.
- `reference/mapping.md`: ADK to Claude Agent SDK, UNVERIFIED.
- test script: lab/stage1/tests/l06_gate.py and out_l06.txt in the course-lab repo (not in this repo).
