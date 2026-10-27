---
name: ccgs-code-review
description: "Read-only architectural review against explicit project constraints, runtime evidence, and performance concerns."
---

Run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow` and use its output.

# Code Review



Every
`native user-input mechanism` call follows `.agents/studio/docs/automation-modes.md`
(collaborative reviews major drafts · guided raises material decisions · autonomous records decisions;
`automation_always_ask` categories always prompt).

## Insufficient input — check this before producing any report

**If the inputs this skill needs do not exist, the answer is "could not run" —
not a filled-in report.** Check first, and stop if the check fails.

1. List the inputs this skill reads (data files, prior reports, profiler output,
   test results, registries, source code).
2. For each, record `FOUND` or `ABSENT` — not "assumed present".
3. If any input required for a section is ABSENT, that section is
   **`NOT ASSESSED — NO DATA`**. Do not estimate it, do not infer it from an
   adjacent artifact, and do not leave a mandated cell to be filled by whoever
   reads the template next.
4. If **every** required input is ABSENT, stop and report
   **`NOT ASSESSED — NO DATA`** as the whole verdict, naming what was missing and
   which skill produces it.

**A verdict of `NOT ASSESSED` is a success.** It is the correct, useful answer to
"what does the data say?" when there is no data. The failure mode this prevents is
specific: a report whose verdict enum has no "could not run" state produces
**false clean passes** — an asset audit returning COMPLIANT on a project with no
assets and no standards, or a performance profile reporting ">99% headroom against
a 16.67ms budget" with zero profiler data and no budget ever set.

**Absence of evidence is never evidence of absence.** A scan that finds no
matches because there are no files to scan has not verified anything. Say which of
the two happened — a reader cannot tell from a green result.

---

## Phase 1: Load Target Files

Read the target file(s) in full. Read AGENTS.md for project coding standards.

---

## Phase 2: Identify Engine Specialists

Read the `specialists` block from `project.yaml`; if it is absent, fall back to the `## Engine Specialists` section of `docs/technical-preferences.md`. Note:

- The **Primary** specialist — `<engine>-specialist` derived from `engine.name` (Godot→`ccgs-godot-specialist`, Unity→`ccgs-unity-specialist`, Unreal→`ccgs-unreal-specialist`); used for architecture and broad engine concerns
- The **Language/Code Specialist** — `specialists.code` — used when reviewing the project's primary language files
- The **Shader Specialist** — `specialists.shader` — used when reviewing shader files
- The **UI Specialist** — `specialists.ui` — used when reviewing UI code

**A value of
ull` means UNSET — treat that key as absent and skip its
specialist. Never spawn it as an agent name.** The v1.0 migration writes
ull`
for any specialist the legacy file did not name, and it writes the whole block
whenever *one* member is set — so a project that configured only its code
specialist carries `shader: null` and `ui: null`. The config reader returns the
four-character string `"null"` for these, which is not empty and therefore reads
as configured.
ull`, empty, and missing are the same state here.

If no engine is configured (no `engine.name` in `project.yaml`, and `technical-preferences.md` reads `[TO BE CONFIGURED]` or is missing), skip engine specialist steps. **Record ``Engine validation: NOT ASSESSED — no engine configured (`engine.name` unset in `project.yaml`)`` in this run's output.** A skipped check that says nothing is indistinguishable from a check that passed; the reader cannot tell engine guidance was never sought.

---

## Phase 3: ADR Compliance Check

**Argument:** `$ccgs-code-review [file(s)]` may optionally include a story file path as the last argument (e.g., `$ccgs-code-review Assets/Scripts/Combat/Attack.cs production/epics/combat/story-001.md`). If a story path is provided, read it to extract the governing ADR reference.

Search for ADR references in, in priority order:
1. The story file (if provided as argument)
2. Header comments at the top of the implementation files
3. Commit messages referencing these files (`git log --oneline -- [file]`)

Look for patterns like `ADR-NNNN` or `docs/architecture/adr-` (either case).

If no ADR references found, note: "No ADR references found — ADR compliance check skipped. For full ADR compliance review, provide the story path: `$ccgs-code-review [files] [story-path]`."

For each referenced ADR, load **only the sections this check needs — never an unbounded full read.** A substantial ADR exceeds the 25k-token `Read` cap, and a capped read's only recovery is paging the remainder — the most expensive way to read a file. Use the same pattern as `$ccgs-dev-story` and `$ccgs-create-stories`:

1. **Map the headings** (cheap — line numbers only): `Grep pattern="^## " path="[adr-file]" output_mode="content" -n`
2. **Bounded-read only `## Decision` and `## Consequences`**, using the line numbers to set `Read(offset, limit)` spans that end where the next heading begins. If the heading map is empty (a nonstandard ADR predating the template), fall back to one full `Read`; if that truncates at the cap, grep for the decision/consequence content directly rather than paging the remainder.

A referenced ADR whose file is missing, or that cannot be read, makes ADR
Compliance `NOT ASSESSED — [ADR] could not be read`: name it. No reference at
all is `NO ADRS FOUND`, a different result.

From those two sections, classify any deviation:

- **ARCHITECTURAL VIOLATION** (BLOCKING): Uses a pattern explicitly rejected in the ADR
- **ADR DRIFT** (WARNING): Meaningfully diverges from the chosen approach without using a forbidden pattern
- **MINOR DEVIATION** (INFO): Small difference from ADR guidance that doesn't affect overall architecture

---

## Phase 4: Standards Compliance

Identify the system category (engine, gameplay, AI, networking, UI, tools) and evaluate:

- [ ] Public methods and classes have doc comments
- [ ] Cyclomatic complexity under 10 per method
- [ ] No method exceeds 40 lines (excluding data declarations)
- [ ] Coupling/ownership causes no concrete correctness problem; do not mandate dependency injection
- [ ] Configuration values loaded from data files
- [ ] Existing system boundaries satisfy the accepted contract; add no interface solely for a checklist

---

## Phase 5: Architecture constraints

**Architecture:**
- [ ] Correct dependency direction (engine <- gameplay, not reverse)
- [ ] No circular dependencies between modules
- [ ] Proper layer separation (UI does not own game state)
- [ ] Events/signals used for cross-system communication
- [ ] Consistent with established patterns in the codebase

**Project-defined architecture constraints:**
- [ ] Respect explicit responsibility boundaries documented by the project
- [ ] Do not require extensibility abstractions unless an ADR requires them
- [ ] Check declared contracts where they exist
- [ ] Do not mandate interfaces without an existing contract
- [ ] Do not force dependency inversion or DI absent an ADR

---

## Phase 6: Game-Specific Concerns

- [ ] Frame-rate independence (delta time usage)
- [ ] No allocations in hot paths (update loops)
- [ ] Proper null/empty state handling
- [ ] Thread safety where required
- [ ] Resource cleanup (no leaks)

---

## Phase 7: Specialist Reviews (Parallel)

Spawn all applicable specialists simultaneously via
`native delegation` — do not wait for one before starting the next.

> **Verify every specialist finding before reporting it. Do not pass findings
> through unchecked.** For each finding, record in the report:
>
> - **File and line** it refers to.
> - **Evidence** — the quoted code, or the concrete input/state that triggers it.
> - **Confidence** — `VERIFIED` (you checked it yourself) or `UNVERIFIED —
>   specialist claim` (you could not).
>
> A finding you could not verify is reported as unverified or dropped, never
> promoted to a defect on the strength of confident phrasing.
>
> **Why this is mandatory.** Agents are reliable when deriving and unreliable when
> diagnosing existing code: a **wrong** claim about a short function can be fluent
> enough to pass a skim, and a claimed bug can fall apart once you enumerate the
> inputs. Without this step the parent review is a laundering channel: a guess
> enters as a specialist finding and leaves as a reviewed defect.

### Engine Specialists

If an engine is configured, determine which specialist applies to each file and spawn in parallel:

- Primary language files (`.gd`, `.cs`, `.cpp`) → Language/Code Specialist
- Shader files (`.gdshader`, `.hlsl`, shader graph) → Shader Specialist
- UI screen/widget code → UI Specialist
- Cross-cutting or unclear → Primary Specialist

Also spawn the **Primary Specialist** for any file touching engine architecture (scene structure, node hierarchy, lifecycle hooks).

### QA Testability Review

For Logic and Integration stories, also route a read-only check to `ccgs-qa-tester` via
`native delegation` in parallel with the engine specialists. Pass:
- The implementation files being reviewed
- The story's `## QA Test Cases` section (the pre-written test specs from ccgs-qa-lead)
- The story's `## Acceptance Criteria`

Ask the ccgs-qa-tester to evaluate:
- [ ] Are all test hooks and interfaces exposed (not hidden behind private/internal access)?
- [ ] Do the QA test cases from the story's `## QA Test Cases` section map to testable code paths?
- [ ] Are any acceptance criteria untestable as implemented (e.g., hardcoded values, no seam for injection)?
- [ ] Does the implementation introduce any new edge cases not covered by the existing QA test cases?
- [ ] Are there any observable side effects that should have a test but don't?

For Visual/Feel and UI stories: ccgs-qa-tester reviews whether the manual verification steps in `## QA Test Cases` are achievable with the implementation as written — e.g., "is the state the manual checker needs to reach actually reachable?"

Collect all specialist findings before producing output.

---

## Phase 8: Output Review

```
## Code Review: [File/System Name]

### Engine Specialist Findings: [N/A — no engine configured / CLEAN / ISSUES FOUND]
[Findings from engine specialist(s), or "No engine configured." if skipped]

### Testability: [N/A — no story path given / N/A — Visual/Feel or Config story / TESTABLE / GAPS / BLOCKING]
[ccgs-qa-tester findings: test hooks, coverage gaps, untestable paths, new edge cases]
[If BLOCKING: implementation must expose [X] before tests in ## QA Test Cases can run]

### ADR Compliance: [NOT ASSESSED / NO ADRS FOUND / COMPLIANT / DRIFT / VIOLATION]
[List each ADR checked, result, and any deviations with severity]

### Standards Compliance: [X/6 passing]
[List failures with line references; a missing doc comment names the method or class]

### Architecture: [NOT ASSESSED / CLEAN / MINOR ISSUES / VIOLATIONS FOUND]
[List specific architectural concerns]

### explicit architecture constraints: [NOT ASSESSED / COMPLIANT / ISSUES FOUND]
[List specific violations]

### Game-Specific Concerns
[List game development specific issues]

### Positive Observations
[What is done well -- always include this section]

The reviewer and any QA specialist are read-only: they do not write QA reports,
story status/content, implementation files, receipts, or session checkpoints.
Return findings to the caller, which retains the response and performs any
authorized follow-up through the normal workflow.

### Required Changes
[Must-fix items before approval — ARCHITECTURAL VIOLATIONs always appear here]

### Suggestions
[Nice-to-have improvements]

### Verdict: [NOT ASSESSED / APPROVED / APPROVED WITH SUGGESTIONS / CHANGES REQUIRED]
```

Choose the verdict, first match wins:
- **CHANGES REQUIRED** — anything under Required Changes
- **NOT ASSESSED** — nothing to review (the no-data path above), the engine
  specialist review did not run — no engine configured, or a specialist that
  could not be spawned — or any report section reads `NOT ASSESSED` (ADR
  Compliance with a referenced ADR that could not be read, Architecture, explicit architecture constraints);
  name which. NOT ASSESSED ranks below CHANGES REQUIRED, because a known
  defect is more actionable than a skipped check, and above both approvals: a
  review that skipped the engine check has not approved the code. (`NO ADRS
  FOUND` is not NOT ASSESSED: with no ADR to check, it does not stop an
  approval.)
- **APPROVED WITH SUGGESTIONS** — only Suggestions
- **APPROVED** — no required changes and no suggestions

This skill is read-only — no files are written.

---

## Phase 9: Next Steps

Use
`native user-input mechanism`:
- Prompt: "Code review complete — verdict: [NOT ASSESSED / APPROVED / APPROVED WITH SUGGESTIONS / CHANGES REQUIRED]. How would you like to proceed?" (the Phase 8 verdict, word for word)
- Options (adjust based on verdict):
  - If APPROVED:
    - `[A] Run $ccgs-story-done to mark the story complete`
    - `[B] Stop here`
  - If APPROVED WITH SUGGESTIONS:
    - `[A] Apply the suggestions, then run $ccgs-story-done`
    - `[B] Run $ccgs-story-done now — suggestions noted for later`
    - `[C] Stop here`
  - If CHANGES REQUIRED:
    - `[A] Fix the issues and re-run $ccgs-code-review`
    - `[B] Run $ccgs-story-done anyway with noted exceptions`
    - `[C] Stop here`
  - If NOT ASSESSED:
    - `[A] Fix what stopped the review (point me at the code, run $ccgs-setup-engine, or fix the unreadable ADR reference), then re-run $ccgs-code-review`
    - `[B] Stop here`

If an ARCHITECTURAL VIOLATION is found:
- If the violation contradicts an **existing ADR**: fix the implementation to comply with `docs/architecture/[adr-file].md`. If the design has legitimately changed, run `$ccgs-architecture-decision` to formally *revise* the existing ADR — do not create a competing one.
- If **no ADR exists** for the pattern that was violated: run `$ccgs-architecture-decision` to document the correct approach before fixing the code.
