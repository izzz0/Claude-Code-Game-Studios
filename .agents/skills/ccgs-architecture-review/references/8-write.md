# Architecture review: read-only artifact handoff

The reviewer returns findings, traceability data and proposed registry changes in
its response. It does not write the review report, RTM, registry, reflexion log,
QA evidence, story status or session checkpoint. This applies in every automation
mode. The coordinator may retain the response and apply authorized changes later.

## Scope and proposed updates

- A `single-gdd` review proposes changes only for the reviewed system. Preserve
  every other system's RTM rows and TR entries. If no RTM exists, explain that a
  full review is needed to construct it; do not invent cross-system coverage.
- Include actual covered/partial/missing requirements, governing ADRs, conflicting
  names and source paths. RTM percentages describe requirement traceability and
  never satisfy a configured code/test coverage threshold.
- List new TR IDs, revised requirement text, proposed deprecations and superseding
  IDs separately. Keep stable IDs, never renumber/delete entries, and flag any
  consequential removal or replacement for a human decision.
- Before returning proposed registry changes, re-read its current content to
  detect concurrent changes. Return a proposal against that version. The
  coordinator must revalidate it before applying and run `registry.sh validate`
  after an authorized update; a reviewer does not perform that update.
- Return only actual architecture conflicts for a proposed reflexion entry,
  including documents, contradictory claims, suggested resolution and reusable
  lesson. Missing ADRs are gaps, not fabricated conflicts.

## Evidence receipt

At the end, run the read-only `review-receipts.sh hash` helper against the actual
reviewed GDDs, ADRs, registries, architecture, engine references and configuration.
Return its stamp lines with the findings. Do not write a receipt file or edit an
input before taking its hash. Missing or unreadable required inputs remain
NOT ASSESSED. A receipt of an optional absent path does not prove that path was
reviewed.

## RTM response format

Return this data inline for `rtm` mode; the coordinator owns any later save:

```markdown
# Requirements Traceability Matrix (RTM)

> Last Updated: [date]
> Mode: $ccgs-architecture-review rtm
> Coverage: [N]% full chain complete (GDD → ADR → Story → Test)

## How to read this matrix

| Column | Meaning |
|--------|---------|
| TR-ID | Stable requirement ID from tr-registry.yaml |
| GDD | Source design document |
| ADR | Architectural decision governing implementation |
| Story | Story file that implements this requirement |
| Test File | Automated test file path |
| Test Status | COVERED / MISSING / NONE / NO STORY |

## Full Traceability Matrix

| TR-ID | GDD | Requirement | ADR | Story | Test File | Status |
|-------|-----|-------------|-----|-------|-----------|--------|
[Full matrix rows from Phase 3b]

## Coverage Summary

| Status | Count | % |
|--------|-------|---|
| COVERED — full chain complete | [N] | [%] |
| MISSING test — story exists, no test | [N] | [%] |
| NO STORY — ADR exists, not yet implemented | [N] | [%] |
| NO ADR — architectural gap | [N] | [%] |
| **Total requirements** | **[N]** | **100%** |

## Uncovered Requirements (Priority Fix List)

Requirements where the full chain is broken, prioritised by layer:

### Foundation layer gaps
[list with suggested action per gap]

### Core layer gaps
[list]

### Feature / Presentation layer gaps
[list — lower priority]

## History

| Date | Full Chain % | Notes |
|------|-------------|-------|
| [date] | [%] | Initial RTM |
```

## Result and next action

Return PASS, CONCERNS, FAIL or NOT ASSESSED with actual evidence and blockers.
PASS permits progression; CONCERNS needs explicit acceptance of the listed risks.
FAIL and NOT ASSESSED retain the stage. A report or proposal existing is not
approval. Include a checkpoint summary in the response for the coordinator;
never update the checkpoint during this review.
