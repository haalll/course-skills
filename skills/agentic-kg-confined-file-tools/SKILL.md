---
name: agentic-kg-confined-file-tools
description: Use when an LLM agent reads local files through tools you write (list, sample, suggest/approve a set of files); covers confining model-supplied paths to one root, validating suggestions against a listing, and capping bytes, with ADK 1.5.0 reference code.
---

# Confined file tools for an agent (DRAFT; throwaway-file and fake-model tests only)

Status: draft on branch `draft/r8`. Checked against google-adk 1.5.0; no live model, no SDK mapping.

## Rules
1. Resolve the model's path first (`..` and symlinks), then require `resolved.is_relative_to(root)`. Rejecting absolute paths and checking existence is NOT confinement. Never use `str.startswith` on paths.
2. The root comes from your code, not from the model. Reject NUL bytes.
3. Cap bytes as well as lines (a single huge line passes a line cap).
4. Offer a listing tool and store only suggested paths that it returned.
5. Suggest -> approve: approval tool with no arguments; do not rely on set + approve in one model response (L06 rules).
6. Residual: link swapped after the check, hard links, sensitive-but-allowed files. Use a read-only copy or a low-privilege uid when it matters.

## Where the detail lives
Card: `agentic-kg-construction/L07-file-suggestions/card.md`. Code: its `reference/`.
