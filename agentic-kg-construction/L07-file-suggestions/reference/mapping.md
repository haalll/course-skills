# L07 mapping to the Claude Agent SDK (DEC-001): UNVERIFIED

- Same shape as L06: custom tools through `tool` + `create_sdk_mcp_server`; the lab only probed that these names import
  in claude-agent-sdk 0.2.165 (I-005). No behaviour was run.
- Idea to test: instead of custom file tools, the built-in Read/Glob limited by permission rules to one directory.
  Not tried; whether a `..` or a symlink escapes those rules is exactly the question this card's gotcha (a) asks. Test with
  throwaway files before relying on it.
- Whatever the framework: resolve the path first, then compare path components against the resolved root.
