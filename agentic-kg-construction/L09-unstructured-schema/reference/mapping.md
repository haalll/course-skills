# L09 mapping to the Claude Agent SDK (DEC-001): UNVERIFIED

- The two agents are two calls in your own orchestration code, entity types approved before the fact step starts [inference, not run].
- The checks move into the tool that stores a fact: approved types looked up in your own store, a missing approval is an error
  that names the missing step, labels compared exactly, predicate normalised, facts kept as a list [inference].
- The post-turn guard (look at the store after the turn, retry with a corrective message, then fail closed) is plain code
  around the call, so it carries over unchanged [inference].
- Whether the SDK runs several tool calls from one response in a way that loses writes was not tested (I-005 covers the L06 gate only).
