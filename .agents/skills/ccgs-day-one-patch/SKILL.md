---
name: ccgs-day-one-patch
description: "Day-one launch patch — focused fix for known issues found after gold master. Mini-sprint with QA gate and rollback."
---

# Day One Patch

Resolve the repository root and effective configuration before acting:
`bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,qa.level,testing.strict,engine_values`.
Read `.agents/studio/docs/core-workflow.md` and the relevant engine reference.

## Release safety

- Check the configured engine, commands, QA evidence, and stage before making a release recommendation. A checklist is evidence collection, not authorization to publish or deploy.
- Preserve unresolved failures and missing evidence as blockers or `NOT ASSESSED`; do not infer approval from a clean-looking document.

## Detailed contract

Read `references/source-contract.md` for the source-derived workflow and artifact contract.
