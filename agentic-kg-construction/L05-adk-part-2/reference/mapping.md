# L05 ADK to Claude Agent SDK (DEC-001): UNVERIFIED, nothing here was checked against SDK docs or code

| ADK 1.5.0 | Candidate in the Claude Agent SDK | Status |
|---|---|---|
| root agent + `sub_agents` | main agent plus subagent definitions whose descriptions drive delegation | inference |
| `transfer_to_agent` hands the turn over, next turn stays with the sub-agent | an SDK subagent is called as a delegated task and returns its result to the caller (likely no persistent hand-over) | inference; if so, ADK's pattern 4 has no equivalent |
| `tool_context.state` | no shared session dict known; keep application state in our own store passed to tools | inference |
| `output_key` | the subagent's returned result, stored by the caller | inference |
