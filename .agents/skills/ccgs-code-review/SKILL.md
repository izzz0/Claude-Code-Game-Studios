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

Return findings, evidence hashes/paths, and one shared-gate verdict in every workflow mode:

- **PASS** — all applicable criteria were assessed with sufficient evidence, with no blocking finding or required evidence left unassessed. The caller may continue to `$ccgs-story-done`, which performs the separate closure check; this review never marks a story complete.
- **CONCERNS** — the review is otherwise assessed, but has named non-blocking risks. State each risk and obtain the user's explicit acceptance before continuing to `$ccgs-story-done`; record accepted risks there.
- **FAIL** — a verified acceptance failure or other blocking finding remains. Route its concrete evidence to `$ccgs-dev-story` for correction, then review again. Never route a failing story to `$ccgs-story-done`.
- **NOT ASSESSED** — a required input, evidence source, or independent review is unavailable. Name each gap and the source or action that can resolve it. Do not route an unassessed story to `$ccgs-story-done` or treat missing evidence as a pass.

If a verified blocker and an unassessed section coexist, report the section as NOT ASSESSED and use FAIL as the overall verdict. Do not ask whether to continue along the ordinary correction and re-review route. This skill remains read-only; the caller decides whether to start another skill.

## Standard/full workflow

Resolve workflow with the command above. For standard or full, read references/full-workflow.md and apply its artifact, review, and evidence phases, subject to .agents/studio/docs/core-workflow.md; minimal remains the default and stops at the minimal contract.
