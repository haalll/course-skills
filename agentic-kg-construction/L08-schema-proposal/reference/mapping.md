# L08 mapping to the Claude Agent SDK (DEC-001): UNVERIFIED

- No LoopAgent equivalent is known. The loop is ordinary orchestration code you own: call the proposer, call the critic,
  test the verdict, stop or repeat, with a hard iteration count [inference, not run].
- Because you own the stop test, the fixes carry over as they are: exact-match verdict, empty or missing verdict is "not
  approved", a returned outcome (`converged` True/False) the caller must handle, feedback cleared at the start of a run.
- Proposer and critic as two subagents is an idea only; no SDK call was made for this card (I-005 covers the L06 gate only).
