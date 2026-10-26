---
name: ccgs-code-review
description: Perform a read-only, evidence-based review of one story's changed files, engine compatibility, scope, and freshness receipts.
---

# Code review

Read .agents/studio/docs/core-workflow.md, resolve the root, the story, and docs/engine-reference/<engine>/VERSION.md.

## Inputs

Story ACs, actual changed files, test/runtime/screenshot evidence, and any prior review receipt. Resolve:
bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,engine_values.

## Actions

- Review read-only; do not edit code, story content, or force DI/interfaces/line-count limits.
- Check scope, AC behavior, engine/version compatibility, parse result, tests, runtime, screenshots, and evidence freshness.
- Run bash .agents/studio/scripts/review-receipts.sh hash <changed-files> and include the output in the review response; use check <receipt-file> <changed-files> when a receipt exists. Verify every mandatory file exists independently.
- Findings cite path/line and classify BLOCKING, ADVISORY, or OUT OF SCOPE. Respect an applicable explicit minimal test waiver, while unavailable mandatory runtime/evidence is NOT ASSESSED.
- Make no file writes, including stamps or checkpoints. Return the review and hashes in the response for ccgs-story-done to retain; keep the story In Review. Identify whether this was self-review or independent review.

## Output

Return findings, evidence hashes/paths, and verdict. No blocking findings route to ccgs-story-done; findings route to ccgs-dev-story.

## Standard/full workflow

Resolve workflow with the command above. For standard or full, read references/full-workflow.md and apply its artifact, review, and evidence phases, subject to .agents/studio/docs/core-workflow.md; minimal remains the default and stops at the minimal contract.