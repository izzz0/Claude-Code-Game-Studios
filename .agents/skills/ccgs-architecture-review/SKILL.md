---
name: ccgs-architecture-review
description: "Traceability matrix mapping GDD requirements to ADRs. Finds gaps, cross-ADR conflicts, engine compatibility. PASS/CONCERNS/NOT ASSESSED/FAIL."
---

Run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow` and use its output.

# Architecture Review

The architecture review validates that the complete body of architectural decisions
covers all game design requirements, is internally consistent, and correctly targets
the project's pinned engine version. It is the quality gate between Technical Setup
and Pre-Production.

**Argument modes:**
- **No argument / `full`**: Full review — all phases
- **`coverage`**: Traceability only — which GDD requirements have no ADR
- **`consistency`**: Cross-ADR conflict detection only
- **`engine`**: Engine compatibility audit only
- **`single-gdd [path]`**: Review architecture coverage for one specific GDD
- **`rtm`**: Requirements Traceability Matrix — extends the standard matrix
  to include story file paths and test file paths; outputs
  `docs/architecture/requirements-traceability.md` with the full
  GDD requirement → ADR → Story → Test chain. Use in Production phase when
  stories and tests exist.

---

Every
`native user-input mechanism` call follows `.agents/studio/docs/automation-modes.md`
(collaborative reviews major drafts · guided raises material decisions · autonomous records decisions;
`automation_always_ask` categories always prompt).

**`workflow`** (see `.agents/studio/docs/workflow-modes.md`):
- `full` — full traceability matrix across all GDDs and all ADRs.
- `standard` — reduced scope: architecture doc + critical ADRs only.
- `minimal` — not applicable (no architecture doc required).

## Phase 1: Load Everything

**Read `references/1-load.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## Phase 2: Extract Technical Requirements from Every GDD

**Read `references/2-extract-requirements.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## Phase 3: Build the Traceability Matrix

**Read `references/3-traceability.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## Phase 4: Cross-ADR Conflict Detection

**Read `references/4-conflicts.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## Phase 5: Engine Compatibility Cross-Check

**Read `references/5-engine.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## Phase 6: Architecture Document Coverage

**Read `references/6-document-coverage.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## Phase 7: Output the Review Report

**Read `references/7-report.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## Phase 8: Write and Update Traceability Index

**Read `references/8-write.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## Phase 9: Handoff

**Read `references/9-handoff.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## Error Recovery Protocol

**First, verify the artifact.** If the return contract named a path, check the
path exists before treating the phase as done — **a named artifact that is not
on disk is a failed phase, however fluent the response reads.** An agent can
burn a full phase and return a plausible preamble having written nothing, which
is neither BLOCKED nor an error nor "fails to complete", so the trigger below
never fires. Resume it naming the unmet contract; the context is
usually still there.

If any spawned agent returns BLOCKED, errors, or fails to complete: **surface it
immediately, don't proceed past a dependency it blocks, and always produce a
partial report** (retry scope here = fewer GDDs / single-system). Full procedure:
`.agents/studio/docs/error-recovery-protocol.md`.

---

## Collaborative protocol

Read silently and return the traceability matrix, findings, evidence hashes and
proposed changes in the response. Review remains read-only in guided,
collaborative and autonomous modes; the coordinator owns authorized artifact
updates after this run. Ask only about ambiguous requirements or consequential
product/architecture decisions. PASS permits progression, CONCERNS requires
explicit human risk acceptance, and FAIL/NOT ASSESSED retains the stage.
