# Project map: where cards might apply

Candidate uses only, not decisions. Kept out of the cards (DEC-005).

| Card | Project | Candidate use | Status |
|---|---|---|---|
| agentic-kg-construction/L04 | Dux knowledge base | Read-only KB tool with the status/error envelope over `/srv/dux-kb`, one agent per strategy. Target the quant DB and trade summaries first; the playbook file is out of scope (DEC-003). | untested idea |
| agentic-kg-construction/L04 | Any tool an LLM fills in (wallet-intel, bscguard SQL/DuckDB lookups) | House rule: parameterised queries plus the envelope. | untested idea |
| agentic-kg-construction/L04 | Agent regression tests | Scripted multi-turn conversations as cheap tests before a long run. | untested idea |
| agentic-kg-construction/L05 | Dux knowledge base | One router agent plus per-strategy specialists with `description`s that say what each does not handle; the final answer is read from the last final event. | untested idea |
| agentic-kg-construction/L05 | Any multi-agent job with shared facts | Keep shared facts in a state store written via tool parameters, read with defaults; one-shot specialists get `disallow_transfer_to_parent`. | untested idea |
| agentic-kg-construction/L06 | Hal's sniper / paper-trading stages | "Perceived plan" vs "approved plan" before any action changes state; approval tool takes no arguments; refuse approval in the turn that wrote the plan. | untested idea |
| agentic-kg-construction/L06 | course-lab itself | The signed approval is the same pattern with the gate outside the model (STATE.md T-011). | untested idea |
| agentic-kg-construction/L07 | Dux knowledge base | An agent that proposes which `/srv/dux-kb` files feed a strategy agent, Hal approving the set; the tools only read inside one root (resolve, then compare). | untested idea |
| agentic-kg-construction/L07 | Any file-reading tool an LLM drives (Hal's other servers) | House rule: resolve the path, compare components against the root, cap bytes; test with `..` and a symlink to a throwaway file. | untested idea |
| agentic-kg-construction/L08 | Hal's trading-plan agents | Proposer drafts, critic checks against data, bounded loop; the stop test is an exact verdict, an empty verdict fails closed, and non-convergence goes to Hal. | untested idea |
| agentic-kg-construction/L08 | Any critic loop (Hal's other servers) | House rule: the loop returns `converged` True/False; nothing downstream acts on a plan whose loop gave up. | untested idea |
