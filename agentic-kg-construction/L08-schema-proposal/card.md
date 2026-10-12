---
course: Agentic Knowledge Graph Construction (DeepLearning.AI x Neo4j), lesson 8 of 12
topic: schema proposal for structured data: a proposer/critic refinement loop (LoopAgent) with an escalation checker
card_version: 5 (round 17: checker also fails a plan that cites a file outside the caller's expected set, tests lab/stage1/r17/l17_extra.py; v4, round 15: checker also requires the caller's expected files all planned, build_loop(expected_files=...); tests lab/stage1/r15/l15_complete.py. v3: stored plan, r12)
status: DRAFT; v5 (unexpected-file check) merged to main in round 19 (draft/r16, desktop review r19); v4 merged r16
pinned_versions: google-adk==1.5.0 (course pin; newer ADK may differ)
verified:
  runtime: "scripted fake models only, no live model (lab/stage1/tests/l08_loop.py, l08_reference_check.py, round 10)"
  static_read: "LoopAgent, AgentTool, output_key and instruction templating read in the 1.5.0 wheel (locators below)"
  sdk_mapping: false      # see reference/mapping.md
  notebook: false         # lesson notebook not captured; the "naive" checker/tools are OUR reconstruction of what the narration describes
---

# L08: proposer + critic in a bounded loop

## When to use this
- A first answer is often good but not reliably right, and a second agent can check it against data.
- You need an automatic review step with a hard iteration limit and a hand-back to a human when it does not converge.
- You build a structured plan (schema, construction rules, trade plan) incrementally through tools, keyed by name.

## Patterns (framework-independent)
Tags: **course** = taught in the lesson (transcript only); **run** = reproduced with scripted fake models; **inference** = our reasoning.

1. **Refinement loop = proposer, critic, checker** [course, run]. A `LoopAgent` runs the three in order, repeatedly: the proposer writes a plan through tools, the critic replies with text only, a small custom checker reads the verdict from state and either escalates (stops the loop) or lets it go round again.
2. **Bounded by `max_iterations`** [course, run]; the lesson uses 2. When the bound is hit the loop just ends; nothing marks it as a give-up (gotcha e).
3. **Critic writes to state with `output_key`** [course, run]: its final text lands in `state["feedback"]`; the proposer's instruction reads it through `{feedback}`. A reply with text `''` stores `''`; a reply with no parts stores nothing (gotcha b).
4. **Escalation is an event action** [course, run]: the checker yields an event with `actions.escalate=True`; `LoopAgent` returns when it sees one (loop_agent.py:52). The sub-agent's own return value plays no part.
5. **Plan built through narrow tools, keyed by name** [course]: propose/remove node and relationship rules, a getter, then an L06-style approve tool.
6. **Verify claims with a search tool** [course]: confirm a column is unique before using it as an id.
7. **Domain expertise in long prompt hints** [course]: node vs relationship files, "full" vs "reference" relationships, "the graph must be connected".
8. **Loop wrapped as a tool for a coordinator** [course, run]: the loop runs in its own inner runner; the parent's state is copied in, state deltas are copied back, and the tool result is the last inner event's text (gotcha g).
9. **Seed or reset state at the start of a run** [course, run]: the lesson seeds `feedback=""`; a `before_agent_callback` on the loop that sets it does the same and also clears a previous run's verdict (gotchas c, f).
10. **Make the outcome explicit** [run, inference]: the checker writes `converged` (True/False) and a text event; the caller acts on that. The checker approves only when the verdict is exactly `valid` AND a plan is stored (see gotcha h).

## Do / don't
- Do make the stop test exact (the critic's whole reply is one token), not a substring.
- Do fail closed: an empty or missing verdict is "not approved".
- Do bound every loop and make "did not converge" a state the caller must handle (a human decides).
- Do key plan entries by name; refuse a duplicate label from a second source file with a corrective error, allow a revision from the same file [run: same file again returns success and keeps the entry; other file errors, lab/stage1/tests/out_l08_revision.txt, which re-states the guard's logic rather than importing it].
- Do reset feedback (and counters) when a new run starts.
- Do give the checker's last event a text, so a coordinator that runs the loop as a tool gets something other than `''`.
- Don't test `"valid" in text`: it also matches "invalid".
- Don't run two plan-writing tool calls in one model response and trust the stored plan: only the last call's state delta is kept (L06 d; seen again below).

## Gotchas
| | Claim | Result (google-adk 1.5.0, round 10, fake models; out_l08.txt) |
|---|---|---|
| a | A `"valid" in feedback` stop also stops on "invalid ..." | **Reproduced on our reconstruction**: critic says `invalid: unique column not confirmed`; the substring checker stops after 1 iteration, the exact-match checker runs a 2nd iteration and stops on `valid` |
| b | Empty or missing feedback counts as valid | **Reproduced**: critic text `''` and a critic reply with no parts both end the loop at iteration 1 with the lesson-style rule; the fail-closed checker runs to the bound with `converged=False`. A critic that raises is not fail-open: the exception propagates out of the run |
| c | `{feedback}` raises KeyError on the first pass | **Reproduced**: `KeyError: Context variable not found: feedback`, proposer never called. Fixes that worked: `{feedback?}` (optional form, renders `''`), a reset callback on the loop, or seeding `feedback=''` (instructions_utils.py:101-104) |
| d | A second file with the same label silently overwrites the first | **Reproduced**: `{'Person': 'b.csv'}` stored, both calls say success; with the duplicate check the second call errors and `{'Person': 'a.csv'}` stays. New: with both calls in ONE model response the second call's error event has an empty delta and wins, so the plan is not stored at all (`nodes=None`) |
| e | Giving up at `max_iterations` looks like convergence | **Reproduced**: with the lesson-style checker a converged run and a gave-up run have the same state keys and the same last event (author checker, no text); the only difference is whether an escalate event exists in the event stream. A caller that only reads state or the tool result cannot tell. The fix (checker writes `converged`, plus text) separates them |
| f | Feedback persists across runs in one session | **Reproduced**: run 2's first proposer instruction contained run 1's `revise: columns wrong`; with the reset callback it was empty |
| g | State written inside a loop run as a tool reaches the coordinator; escalate stops the inner loop | **Reproduced, with one trap.** `AgentTool` runs the loop in a fresh inner runner seeded with a copy of the parent's state (agent_tool.py:120-124) and copies only `state_delta` back (:131-132): `nodes`, `feedback`, `converged` reached the parent; the parent's `goal` was visible inside. `escalate` ended the inner loop (1 proposer iteration of 3) and does not reach the parent's event stream; the coordinator carried on. The trap: the tool result is the last inner event's text (:135-137); the lesson-style checker's last event has none, so the coordinator got `''` in both the converged and the gave-up case. With the checker's text it got `APPROVED` / `NOT_CONVERGED after 2 round(s)` |
| h | A critic's `valid` plus `converged=True` means a plan exists | **Reproduced on fake models, round 12 (lab/stage1/r12/out_l12_before.txt vs out_l12_after.txt).** Two `propose_node` calls in one response, the second refused: `nodes` is not stored, the critic says `valid`, the old checker gives `converged=True` and text `APPROVED`. A checker that tests the plan ends with `converged=False` and `NOT_CONVERGED after 2 round(s): critic approved but no plan is stored`; a stored plan plus `valid` still converges, `revise:` still does not. **Trap inside the fix:** reading `ctx.session.state` in the checker does NOT work: it is the live dict, and `State.__setitem__` writes it directly (state.py:44), so it still holds the writes ADK drops from the persisted delta (the first try of the fix left `converged=True`). Read the persisted copy with `ctx.session_service.get_session(...)` |

Also seen: every early `escalate` printed an OpenTelemetry "Failed to detach context" traceback on stderr (13 such messages in one run of l08_loop.py, 4 in l08_reference_check.py, whose 4 approving runs stop early; the results were unaffected; cause not investigated).

## Live notes (round 11: reference loop, real Sonnet as proposer AND critic through ADK 1.5.0, n=3, lab/stage1/live/out_l08-*.txt)
- The critic's reply was exactly `valid` (5 characters, nothing else) in 3 of 3 runs, so the exact-match checker approved at iteration 1 each time. No chatty or punctuated approval, no `revise:` reply was seen; the cost of a chatty approval (extra iterations) was therefore not observed.
- Run l08-2 (two files, both told to use label `Person`): the proposer put both calls in ONE response, the second was refused as a duplicate, and ADK kept only that last (refused) call's writes, so NO plan was stored (final state has no `nodes`). The proposer's text said "only half went through"; the critic still replied `valid` and the checker wrote `converged=True`. This is gotcha d meeting gotcha e: `converged=True` does not mean a plan exists. Make the checker also require a non-empty plan in state.
- The checker's text event never reached a later pass (all three runs ended at iteration 1), so its effect on a real model's history is still unmeasured. Cost of the 3 runs about $0.025.

## Residual risks, not tested
- A real critic model on harder plans: only three easy prompts were run and all approvals were exact `valid`. A fail-closed checker turns a chatty approval into a non-approval; that costs iterations, not safety.
- A refused duplicate does not make the plan right: the proposer must react to the error (in the check, the converged plan lacked the second file's rule).
- The checker's text event enters the other agents' history on the next pass (scripted replay, r15, lab/stage1/r15/out_l15_textevent.txt: the proposer's next request carries `[checker] said: NOT_CONVERGED ... plan leaves ['parts.csv'] unplanned`; without the event it carries only `[critic] said: valid`). How a real model reacts to that text was not measured.
- Completeness (v4): the expected set comes from the caller, `build_loop(..., expected_files=...)` is required and refuses an empty set; the checker names the unplanned files in its text. Before/after on fake models: lab/stage1/r15/out_l15_complete.txt (before: `valid` with parts.csv unplanned converged; after: not converged, completed in pass 2 converges). Unexpected files (v5): a stored node rule citing a file outside `expected_files` also stops convergence and is named in the checker text; before/after on fake models: lab/stage1/r17/out_l17_before.txt, out_l17_after.txt. Not covered: a file that is planned wrongly (right file, wrong label) is still the critic's job. The same shape (caller-owned expected ids, one whole-plan tool call) was used on real records in N25 (lab/n25/n25_loop.py).
- The lesson's own code and notebook were not read.

## Mapping to the Claude Agent SDK (DEC-001)
Unverified. See `reference/mapping.md`.

## Where it applies
See `project-map.md`.
