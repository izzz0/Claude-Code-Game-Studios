---
name: ccgs-design-review
description: "Reviews one design document for completeness, internal consistency, implementability, and design standards. Before handing to programmers."
---

Run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow` and use its output.

Run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow` and use its output.
the pre-1.1 name for the same flag: treat `--depth <mode>` exactly as
`--review <mode>`, and say once that it was renamed. Given both, `--review`
wins and `--depth` is ignored — say so. No block → defaults in
`.agents/studio/docs/config-resolution.md`.

# Design Review


## Phase 0: Parse Arguments


See `.agents/studio/docs/director-gates.md` for the full check pattern. Individual gate definitions live in `.agents/studio/docs/director-gates/[gate-id].md` — the spawned agent reads its own gate file; do not read it in the parent session.


Every
`native user-input mechanism` call follows `.agents/studio/docs/automation-modes.md`
(collaborative reviews major drafts · guided raises material decisions · autonomous records decisions;
`automation_always_ask` categories always prompt).

**`workflow`** for the GDD under review — use the `system_overrides` row for `<system>` if the block lists one, else the project value. Validation scope follows the tier:
- `full` — all 8 sections validated; any missing section blocks approval.
- `standard` — the 5 required sections (Overview, Detailed Rules, Edge Cases,
  Dependencies, Acceptance Criteria) block if missing; Formulas blocks only when
  the system defines numeric rules (rates, curves, thresholds, costs — the
  category is a hint, not the test); Player Fantasy and
  Tuning Knobs are advisory (warn, never block) unless `workflow_overrides`
  require them.
- `minimal` — no GDD is expected; if one exists, validate the 5 standard
  sections advisorily.

Resolved mode controls how thorough this review is:

- **`full`**: Complete review — all phases + specialist agent delegation (Phase 3b)
- **`lean`**: All phases, no specialist agents — faster, single-session analysis
- **`solo`**: Phases 1-4 only, no delegation, no Phase 5 next-step prompt — use when called from within another skill

---

## Phase 1: Load Documents

**Freshness check first — a re-review of an unchanged document costs full
price and reproduces the same verdict.** Run:

```
Bash: bash .agents/studio/scripts/review-receipts.sh check "design/gdd/reviews/[doc-name]-review-log.md" "[target-doc-path]" "design/registry/entities.yaml" ".agents/skills/ccgs-design-review/SKILL.md"
```

The registry is in the check because this review consults it for
cross-document facts — an unchanged GDD reviewed against a *changed*
registry can reach different conclusions, so the skip is only safe when
**every** line reads `UNCHANGED` (a registry that never existed doesn't
appear in the output and doesn't block the skip). This skill's file is in it
because a changed skill reviews differently. The check also compares every
other file the log stamps — the related GDDs, concept or brief and narrative
files earlier reviews read — and prints `GONE:` for one that no longer exists.

Then read the latest entry's `Review mode:` line. That review **covers** this
run only when its mode is the same as or deeper than the mode resolved now
(`full` > `lean` > `solo`) and its workflow is the same or deeper (`full` >
`standard` > `minimal`). An entry without the line was written before it
existed and covers nothing.

- **All `UNCHANGED`** and the log's latest entry carries a verdict — surface it:
  *"This document is byte-identical to its last review on [date] ([mode]
  review, verdict: [verdict])."* If that verdict was APPROVED and that review
  covers this run, offer via
`native user-input mechanism`:
  `[A] Use the prior verdict (Recommended)` / `[B] Re-review anyway` —
  `guided` proceeds with [A] and notes it; `autonomous` logs via
  `log_decision` and uses the prior verdict. If it was APPROVED but the
  review asked for now is deeper than the logged one, say so — *"That was a
  [mode] review at workflow [tier]; this run asks for [mode] at [tier]."* —
  and offer `[A] Re-review at [mode] (Recommended)` / `[B] Use the prior
  [mode] verdict`; `guided` and `autonomous` re-review (`autonomous` logs it
  via `log_decision`). If it was NEEDS REVISION or
  MAJOR REVISION NEEDED, say so plainly: the document has not changed since
  it failed review — the prior findings stand; revising the document is the
  next step, not re-reviewing it. Offer to display the prior findings from
  the log.
- **The target doc and this skill's file `UNCHANGED`, and only the registry or
  another stamped cross-document file `CHANGED`, `NEW` or `GONE`** — the prior
  verdict stands except for cross-document facts: re-verify the doc's values
  against the changed files and re-issue the verdict; escalate to a full
  re-review if a conflict appears or that review does not cover this run.
- **Target doc or this skill's file `CHANGED` or `NEW`, or `RECEIPT: NONE`** —
  proceed with the full review below. **Do not offer a partial/delta re-review that skips
  reading or re-analyzing unchanged sections.** A section-scoped re-review
  misses defects a full review finds, and saves little or nothing.
  "Unchanged since last review" only means
  byte-identical to what was reviewed then — it says nothing about whether
  that prior pass was itself complete, and attention narrows to the flagged
  change even under an instruction to scan everything anyway.

Read the target design document in full. This step needs the whole GDD: read it in ranges by its headings (found with the Grep tool: pattern `^#`, content mode), since a whole-file Read over 40 KB is refused. Read AGENTS.md to understand project context and standards.

**For cross-document facts, prefer the registry over sibling GDDs.** If
`design/registry/entities.yaml` exists **and lists entries for this system**,
grep it — these are the established facts this GDD must not contradict, and they
replace reading sibling GDDs to rediscover them:
```
Grep pattern="source: design/gdd/[system].md" path="design/registry/entities.yaml" output_mode="content" -A 6
Grep pattern="design/gdd/[system].md" path="design/registry/entities.yaml" output_mode="content" -B 8
```
The first finds entries this system **owns** — the `-A 6` context includes their
`referenced_by:` block. The second finds entries that **reference** this system —
`referenced_by:` is a block sequence (the key and its paths are on separate
lines), so match the path with `-B 8` context to see the owning entry, not a
`referenced_by.*name` one-liner (which never matches the block form).

**If `design/registry/entities.yaml` does not exist, or lists no entry for this
system** — the file ships as an empty stub, so this is the default until
`$ccgs-design-system` has populated it — fall back to reading the related GDDs the
target doc names in its Dependencies section. Bound the read to those, not to
everything "implied". Do not glob-read all of `design/gdd/`.

**Dependency graph validation:** For every system listed in the Dependencies section, use Glob to check whether its GDD file exists in `design/gdd/`. Flag any that don't exist yet — these are broken references that downstream authors will hit.

**Lore/narrative alignment:** If `design/gdd/game-concept.md` (or, at `rigor: minimal`, the one-page brief `design/game-brief.md`) or any file in `design/narrative/` exists, read it. Note any mechanical choices in this GDD that contradict established world rules, tone, or design pillars. Pass this context to `ccgs-game-designer` in Phase 3b.

**Prior review check:** Check whether `design/gdd/reviews/[doc-name]-review-log.md` exists. If it does, read the most recent entry — note what verdict was given and what blocking items were listed. This session is a re-review; track whether prior items were addressed.

---

## Phase 2: Completeness Check

**Step 2a — gather section presence deterministically (no document read):**

```
Bash: bash .agents/studio/scripts/gdd-structure-check.sh [target-doc-path]
```

It prints a `PRESENT:` list and, when applicable, an `ABSENT:` list and a
`PLACEHOLDER:` list (present sections holding only `[To be designed]`: not yet
written, so treat them as missing for the checklist). It reports
**presence only** and makes no REQUIRED/ADVISORY judgment — that is Step 2b's
job. It already accepts `## Detailed Design` as satisfying the `Detailed Rules`
requirement, so do not flag that as missing.

**Step 2b — apply the tier.** Using the Step 2a lists, evaluate against the
Design Document Standard checklist below. **Mark each section REQUIRED or
ADVISORY per the resolved workflow tier (Phase 0).** A missing REQUIRED section
blocks approval; a missing ADVISORY section is surfaced as a recommendation but
does not block.

A section reported PRESENT can still fail review if it is an empty heading —
spot-read any section the verdict actually turns on.

- [ ] Has Overview section (one-paragraph summary) — REQUIRED at all tiers
- [ ] Has Player Fantasy section (intended feeling) — REQUIRED at `full`; ADVISORY at `standard`
- [ ] Has Detailed Rules section (unambiguous mechanics) — REQUIRED at `full`/`standard`. The GDD template titles this section `## Detailed Design` (it carries Core Rules / States / Interactions sub-headings); accept **either** heading as satisfying this requirement — do not flag "Detailed Rules" as missing when a `## Detailed Design` section is present.
- [ ] Has Formulas section (all math defined with variables) — REQUIRED at `full`; at `standard` REQUIRED whenever the system defines numeric rules (rates, curves, thresholds, costs, damage, drop weights), else ADVISORY. The system's `Category` is a hint, not the test — do not clear this on a category token alone
- [ ] Has Edge Cases section (unusual situations handled) — REQUIRED at `full`/`standard`
- [ ] Has Dependencies section (other systems listed) — REQUIRED at `full`/`standard`
- [ ] Has Tuning Knobs section (configurable values identified) — REQUIRED at `full`; ADVISORY at `standard` unless `workflow_overrides.tuning_knobs`
- [ ] Has Acceptance Criteria section (testable success conditions) — REQUIRED at `full`/`standard`

---

## Phase 3: Consistency and Implementability

**Internal consistency:**
- Do the formulas produce values that match the described behavior?
- Do edge cases contradict the main rules?
- Are dependencies bidirectional (does the other system know about this one)?

**Implementability:**
- Are the rules precise enough for a programmer to implement without guessing?
- Are there any "hand-wave" sections where details are missing?
- Are performance implications considered?
- Is every acceptance criterion independently testable? Flag each one that is
  not, quoting it — "feels balanced", "works correctly", "performs well" are not
  criteria — with a measurable rewrite. In `full` mode `ccgs-qa-lead` also checks them
  (Phase 3b); in `lean` and `solo` no specialist runs, so this main-review check
  is the only one.

**Cross-system consistency:**
- Does this conflict with any existing mechanic?
- Does this create unintended interactions with other systems?
- Is this consistent with the game's established tone and pillars?

**Registry values, wherever the GDD states them.** A value restated in a table,
a catalogue entry or a variant note contradicts the registry as surely as one in
Detailed Rules, and reading by section makes those bodies easy to skim. List the
registry's entry names (`grep -E '^  - name:' design/registry/entities.yaml`),
then search the whole target document once for all of them plus the numeric
keys they carry, case-insensitive, writing each `_` as `[_ ]` so `goblin_scout`
also matches "Goblin scouts":

```
grep -n -i -E 'goblin[_ ]scout|iron[_ ]sword|health|value[_ ]gold' [target-doc-path]
```

Check every line it prints against the registry, whatever section it sits in.
A line that gives an entry a different value, even for one room, variant, level
or exception, contradicts the owning GDD: list it under Required Before
Implementation with its line number, this document's value and the registry's.
With no registry entries, run the same search for the entities and values the
related GDDs define.

---

## Phase 3b: Adversarial Specialist Review (full mode only)

**Skip this phase in `lean` or `solo` mode.**

**This phase is MANDATORY in full mode.** Do not skip it.

**Before spawning any agents**, print this notice:
> "Full review: spawning specialist agents in parallel. This typically takes 8–15 minutes. Use `--review lean` for faster single-session analysis."

### Step 1 — Identify all domains the GDD touches

Using the GDD **already loaded in Phase 1** — do not re-read it — identify every domain present. A GDD can touch multiple domains simultaneously — be thorough. Common signals:

| If the GDD contains... | Spawn these agents |
|------------------------|-------------------|
| Costs, prices, drops, rewards, economy | `ccgs-economy-designer` |
| Combat stats, damage, health, DPS | `ccgs-game-designer`, `ccgs-systems-designer` |
| AI behaviour, pathfinding, targeting | `ccgs-ai-programmer` |
| Level layout, spawning, wave structure | `ccgs-level-designer` |
| Player progression, XP, unlocks | `ccgs-economy-designer`, `ccgs-game-designer` |
| UI, HUD, menus, player-facing displays | `ccgs-ux-designer`, `ccgs-ui-programmer` |
| Dialogue, quests, story, lore | `ccgs-narrative-director` |
| Animation, feel, timing, juice | `ccgs-gameplay-programmer` |
| Multiplayer, sync, replication | `ccgs-network-programmer` |
| Audio cues, music triggers | `ccgs-audio-director` |
| Performance, draw calls, memory | `ccgs-performance-analyst` |
| Engine-specific patterns or APIs | Primary engine specialist (`<engine>-specialist` from `engine.name` — Godot→`ccgs-godot-specialist`, Unity→`ccgs-unity-specialist`, Unreal→`ccgs-unreal-specialist`; fall back to the Primary line of `## Engine Specialists` in `technical-preferences.md`) |
| Acceptance criteria, test coverage | `ccgs-qa-lead` |
| Data schema, resource structure | `ccgs-systems-designer` |
| Any gameplay system | `ccgs-game-designer` (always) |

Spawn `ccgs-game-designer` for all GDDs that describe gameplay mechanics or player-facing rules.
Spawn `ccgs-systems-designer` for all GDDs that contain formulas or system interaction rules.
These are the most common baselines — but not required for pure UI specs, audio specs, or lore documents. Use the domain table above to determine which specialists are truly relevant.

### Step 2 — Spawn all relevant specialists in parallel

**CRITICAL:
`native delegation` in this skill routes a separate independent Codex run
with its own context window. It is NOT task tracking. Do NOT simulate specialist
perspectives internally. Do NOT reason through domain views yourself. You MUST issue
actual
`native delegation` calls. A simulated review is not a specialist review.**

Issue all
`native delegation` calls simultaneously. Do NOT spawn one at a time.

**Prompt each specialist adversarially:**
> "Here is the GDD for [system] and the main review's structural findings so far.
> Your job is NOT to validate this design — your job is to find problems.
> Challenge the design choices from your domain expertise. What is wrong,
> underspecified, likely to cause problems, or missing entirely?
> Be specific and critical. Disagreement with the main review is welcome.
> Read the GDD by section: find the headings with the Grep tool (pattern `^#`,
> content mode) and Read those ranges with offset and limit."

**Additional instructions per agent type:**

- **`ccgs-game-designer`**: Anchor your review to the Player Fantasy stated in Section B of this GDD. Does this design actually deliver that fantasy? Would a player feel the intended experience? Flag any rules that serve implementability but undermine the stated feeling.

- **`ccgs-systems-designer`**: For every formula in the GDD, plug in boundary values (minimum and maximum plausible inputs). Report whether any outputs go degenerate — negative values, division by zero, infinity, or nonsensical results at the extremes.

- **`ccgs-qa-lead`**: Review every acceptance criterion. Flag any that are not independently testable — phrases like "feels balanced", "works correctly", "performs well" are not ACs. Suggest concrete rewrites for any that fail this test.

### Step 3 — Senior lead review

After all specialists respond, spawn `ccgs-creative-director` as the **senior reviewer**:
- Provide: the GDD, all specialist findings, any disagreements between them
- Ask: "Synthesise these findings. What are the most important issues? Do you agree with the specialists? What is your overall verdict on this design — APPROVED, NEEDS REVISION or MAJOR REVISION NEEDED?"
- The ccgs-creative-director's synthesis becomes the **final verdict** in Phase 4, in this skill's verdict words — never a director-gate word such as READY or REJECT.

### Step 4 — Surface disagreements

If specialists disagree with each other or with the ccgs-creative-director, do NOT silently pick one view. Present the disagreement explicitly in Phase 4 so the user can adjudicate.

Mark every finding with its source: `[ccgs-game-designer]`, `[ccgs-economy-designer]`, `[ccgs-creative-director]` etc.

---

## Phase 4: Output Review

```
## Design Review: [Document Title]
Specialists consulted: [list agents spawned]
Re-review: [Yes — prior verdict was X on YYYY-MM-DD / No — first review]

### Completeness: [X/N sections present, where N is the count REQUIRED at this project's `modes.workflow`]
[List only sections missing that are REQUIRED at this tier. Mark ADVISORY gaps
separately as "advisory at `standard`" — do not list them as missing.]

> **N is not 8 unless `workflow: full`.** The tier table earlier in this skill is
> authoritative: 8 required at `full`, 5 at `standard` (+ Formulas when the system
> defines numeric rules), 0 at `minimal`. Do not hardcode `/8` here: reporting a
> `standard` project as "5/8 missing Player Fantasy, Formulas, Tuning Knobs"
> warns about three sections that project's own configuration says it does not
> need, which trains the reader to ignore the review.

### Dependency Graph
[List each declared dependency and whether its GDD file exists on disk]
- ✓ enemy-definition-data.md — exists
- ✗ loot-system.md — NOT FOUND (file does not exist yet)

### Registry Values
[The whole-document search from Phase 3: the terms searched, how many lines it
printed, and each conflict with its line number. With nothing to search, say so:
"No registry entries or related-GDD values: values not cross-checked."]

### Required Before Implementation
[Numbered list — blocking issues only. Each item tagged with source agent.]

### Recommended Revisions
[Numbered list — important but not blocking. Source-tagged.]

### Specialist Disagreements
[Any cases where agents disagreed with each other or with the main review.
Present both sides — do not silently resolve.]

### Nice-to-Have
[Minor improvements, low priority.]

### Senior Verdict [ccgs-creative-director]
[Creative director's synthesis and overall assessment.]

### Scope Signal
Estimate implementation scope based on: dependency count, formula count,
systems touched, and whether new ADRs are required.
- **S** — single system, no formulas, no new ADRs, <3 dependencies
- **M** — moderate complexity, 1-2 formulas, 3-6 dependencies
- **L** — multi-system integration, 3+ formulas, may require new ADR
- **XL** — cross-cutting concern, 5+ dependencies, multiple new ADRs likely
Label clearly: "Rough scope signal: M (ccgs-producer should verify before sprint planning)"

### Verdict: [APPROVED / NEEDS REVISION / MAJOR REVISION NEEDED / NOT ASSESSED]

> **`NOT ASSESSED` when the review could not actually be performed.**
> The other three verdicts are all claims about the design's quality, so each one
> asserts that the document was read and judged. Use `NOT ASSESSED` instead when
> the target document is absent, unreadable, or empty of the sections being
> reviewed, or when a document it depends on is missing so the criteria cannot be
> applied. **Name what was unavailable and which skill produces it.**
>
> `APPROVED` is the dangerous default here: a review that could not find its
> input has not approved anything, and this verdict is consumed downstream as a
> sign-off. `NOT ASSESSED` outranks `APPROVED` in any aggregate — it does not
> outrank the two revision verdicts, because a known problem is more actionable
> than an unknown one.
```

This skill is read-only — no files are written during Phase 4.

---

## Phase 5: Read-only Findings and Handoff

Return the completed review in the response. Do not revise the GDD, update the
systems index, append a review log, write QA evidence or change a checkpoint.
An authorized coordinator may retain this response after the review ends.

Include the target, reviewed scope, workflow and review mode, actual independent
reviewer identities, Required Before Implementation findings, advisory findings,
prior verdict resolution, and hashes of every input used for cross-document
facts. Compute current hashes with:

    bash .agents/studio/scripts/review-receipts.sh hash "[target-doc-path]" "design/registry/entities.yaml" ".agents/skills/ccgs-design-review/SKILL.md" [other actual inputs]

A missing path is not stamped and must be reported. Retained findings may be
reused only while all their stamped inputs remain unchanged; editing behavior
or requirements invalidates the affected findings.

Return proposed systems-index status and review-log content as a handoff, never
apply them inside this review. APPROVED maps to PASS. Advisory CONCERNS require
explicit human acceptance of the listed risks before advancing. Blocking
revisions map to FAIL; missing input or independent review remains NOT ASSESSED.
No review verdict itself changes the project stage.

Read the systems index to recommend an actual next step: fix blockers in a
separate authorized design task, review another pending GDD, run
`$ccgs-consistency-check`, run `$ccgs-review-all-gdds` when multiple GDDs exist,
or design the next named system. Do not start the next skill automatically.
Re-review revisions with a separate non-implementing execution when required.
Do not invent host context percentages or require a host-specific clear command.
