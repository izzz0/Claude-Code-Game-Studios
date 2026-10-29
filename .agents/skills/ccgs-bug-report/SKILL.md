---
name: ccgs-bug-report
description: "Structured bug report from a description, or analyze code for potential bugs. Reproduction steps, severity."
---

# Bug Report

Resolve the repository root and effective configuration before acting:
`bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,qa.level,testing.strict,engine_values`.
Read `.agents/studio/docs/core-workflow.md` and the relevant engine reference.

## Execution contract

- Resolve the repository root and effective configuration before acting; read `.agents/studio/docs/core-workflow.md` and the relevant reference before interpreting project state.
- Keep changes inside the requested artifact scope. Review and audit modes are read-only and return findings with evidence; do not self-approve.
- Inherit the parent model, permissions, provider, sandbox, and tools. Do not pin models or invoke source-host-specific tools; normal authorized edits do not need a separate approval for each file.

## Detailed contract

Read `references/source-contract.md` for the source-derived workflow and artifact contract.
