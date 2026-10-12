---
course: Agentic Knowledge Graph Construction (DeepLearning.AI x Neo4j), lesson 7 of 12
topic: file-suggestion agent: read the approved goal from state, inspect files with bounded tools, suggest -> approve
card_version: 3 (v2 round 9; round 10: pattern 5 tag and a gate rule added after review)
status: MERGED to main in round 10 (desktop review); two review nits applied on draft/r9
pinned_versions: google-adk==1.5.0 (course pin; newer ADK may differ)
verified:
  runtime: "path, size and state checks on throwaway files and scripted fake models only, no live model (lab/stage1/tests/l07_files.py, l07_reference_check.py, round 9)"
  static_read: false      # no ADK source reading this round beyond what L06 already read
  sdk_mapping: false      # see reference/mapping.md (I-005)
  notebook: false         # lesson notebook not captured; the lesson's own tool code was never seen, the "naive" tools below are OUR reconstruction of what the narration describes
---

# L07: a file-suggestion agent fed by state, not by chat history

## When to use this
- A downstream agent must act on a decision made earlier (an approved goal) without re-reading the conversation.
- An agent needs to look at local files to choose inputs, under limits you control.
- Any "propose a set, user approves the set" step (files, columns, tickers, data sources).
Builds on L06 (approval gate built from two tools).

## Patterns (framework-independent)
Tags: **course** = taught in the lesson (transcript only); **run** = reproduced on throwaway files or with a scripted fake model; **inference** = our reasoning.

1. **Read upstream decisions from state through a tool** [course]. The agent calls `get_approved_user_goal` instead of relying on chat history; the instruction says to do so first.
2. **Bounded inspection tools** [course, run]: `list_import_files` (relative paths under one import directory, also saved to state) and `sample_file` (at most ~100 lines). The model sees a capped window, never a whole file.
3. **Confine paths to one root by resolving first** [run]. Rejecting absolute paths and checking existence is not enough: `../x`, `sub/../../x` and a symlink inside the directory that points outside all read the outside file. Resolve (`..` and links), then compare path components with `is_relative_to`; a `startswith` on the string also admits a sibling such as `import_evil` (scenario a).
4. **Re-read your own suggestion from state before presenting it** [course]. The user approves what is stored, not what the model recalls.
5. **Suggest -> approve pair, same shape as L06** [course, run]: `set_suggested_files(list)`, then argument-free `approve_suggested_files`. The set + approve pair was run (gotcha d); "approve errors if nothing is suggested" is [course] only, not run.
6. **Validate the suggestion against the listing** [run]. Store only paths that `list_import_files` returned; the lesson skips this on purpose, and without it an invented path is stored as "suggested" (scenario b).
7. **Cap bytes as well as lines** [run]. A 100-line cap does not bound a file with one 3 MB line (scenario c).
8. **Domain hint in the instruction** [course]: "only structured files (CSV, JSON)".
9. **Seed state to test an agent in isolation** [course]: create the session with an approved goal already in state.
10. **Feedback loop in the directions** [course]: if the user objects, start again from step 1 with the feedback.

## Do / don't
- Do resolve every model-supplied path against the root and check it stays inside; take the root from code, never from the model.
- Do validate a suggested list against the listed files before storing it.
- Do cap lines and bytes, and say so in the docstring.
- Do return corrective error text that names what to do next.
- Do keep a gate's approve out of the model response that wrote the set: refuse when `suggested_files` was written in this turn, or require two turns (L06 d; gotcha d below shows what is lost otherwise).
- Don't let the model's memory of its own suggestion stand in for the stored value.
- Don't treat the resolved-path check as a full sandbox: see the residual risks.

## Gotchas
| | Claim | Result (google-adk 1.5.0 where ADK is involved; round 9, fake models, throwaway files) |
|---|---|---|
| a | Existence check + "no absolute path" lets `../` and links out of the import directory | **Reproduced on our reconstruction** (not the lesson's code, which is unseen): `../outside`, `sub/../../outside`, a link to an outside file (top level and nested) and `../import_evil/c.txt` were all read; a resolved-path check refused each, still read `a.csv`, `sub/b.json` and a link that stays inside. `/etc/hostname` was refused by both. out_l07.txt |
| b | `set_suggested_files` stores invented paths | **Reproduced**: `['a.csv','invented.csv']` stored with status success; with a check against the listing the call returns an error and state stays empty |
| c | No byte cap: one huge line floods the context | **Reproduced**: 3,000,001 chars returned with only a line cap; 20,000 with a byte cap |
| d | L06 one-response overwrite applies here | **Reproduced**: with set + approve in one model response, `approved_files` is stored but `suggested_files` is not (the last `state_delta` wins). Two calls in sequence store both |

## Residual risks, not tested
- A link swapped between the check and the open (race); hard links; a path that is allowed but sensitive. Use a dedicated read-only copy of the files or a low-privilege uid when the content matters.
- Real model behaviour: whether a real model asks for `..` paths, skips non-structured files, or writes an invented list was not run.
- The lesson's own tool code and notebook were not read; claim a rests on the narration as relayed by the desktop draft.

## Mapping to the Claude Agent SDK (DEC-001)
Unverified. See `reference/mapping.md`.

## Where it applies
See `project-map.md` (kept out of the card).
