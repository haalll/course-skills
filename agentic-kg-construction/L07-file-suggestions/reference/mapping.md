# L07 mapping to the Claude Agent SDK (DEC-001): UNVERIFIED

- Same shape as L06: custom tools through `tool` + `create_sdk_mcp_server`; the lab only probed that these names import
  in claude-agent-sdk 0.2.165 (I-005). No behaviour was run.
- Idea to test: instead of custom file tools, the built-in Read/Glob limited by permission rules to one directory.
  Not tried; whether a `..` or a symlink escapes those rules is exactly the question this card's gotcha (a) asks. Test with
  throwaway files before relying on it.
- Whatever the framework: resolve the path first, then compare path components against the resolved root.

## Round 11 live smoke (claude-agent-sdk 0.2.165, sonnet through the proxy, throwaway tree, lab/sdk/smoke_l07.py; n=1 per case, NO control run)
Setup: `tools=["Read"]`, `allowed_tools=["Read(//<folder>/**)"]`, a `can_use_tool` callback that logs and denies, a PreToolUse hook that logs the path.
- `..` path string: the hook already saw the path normalised to `<tmp>/outside_secret.txt` (the CLI collapsed the `..` before the hook). The call was then stopped by a safety classifier in the harness before the permission callback ran, so this case does not tell us what the rule does. The marker did not reach the model.
- A link inside the folder pointing outside: the rule did NOT auto-allow it (the `can_use_tool` callback was reached; the link's own path is inside the folder), which suggests the CLI resolves links when matching rules. Without a control run (a plain file in the folder reading without the callback) we cannot rule out that the rule never matches anything; that control was not run (D4 limit of 3 runs).
- Same link with a PreToolUse hook that checks `realpath`: the hook denied it ("Path resolves outside the import folder"); the marker did not reach the model.
- Costs: 0.0117, 0.0040, 0.0049 USD by proxy delta. The hook's `realpath` check remains a safe belt whatever the rules do.
