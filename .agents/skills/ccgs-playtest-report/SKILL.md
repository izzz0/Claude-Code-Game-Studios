---
name: ccgs-playtest-report
description: "Structured playtest report template, or turn existing playtest notes into structured feedback."
---

Run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow` and use its output.

Run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow` and use its output.
block → defaults in `.agents/studio/docs/config-resolution.md`.

# Playtest Report



## Phase 1: Parse Arguments


See `.agents/studio/docs/director-gates.md` for the full check pattern. Individual gate definitions live in `.agents/studio/docs/director-gates/[gate-id].md` — the spawned agent reads its own gate file; do not read it in the parent session.


Every
`native user-input mechanism` call follows `.agents/studio/docs/automation-modes.md`
(collaborative reviews major drafts · guided raises material decisions · autonomous records decisions;
`automation_always_ask` categories always prompt).

Determine the mode:

- `new` → generate a blank playtest report template. This mode ends after
  Phase 2A: a blank template has nothing to route, review or save.
- `analyze [path]` → read raw notes and fill in the template with structured findings
- No argument → ask via
`native user-input mechanism`: `[A] New blank template` /
  `[B] Analyze notes — I'll give you the path`

---

## Phase 2A: New Template Mode

Generate this template and output it to the user:

```markdown
# Playtest Report

## Session Info
- **Date**: [Date]
- **Build**: [Version/Commit]
- **Duration**: [Time played]
- **Tester**: [Name/ID]
- **Platform**: [PC/Console/Mobile]
- **Input Method**: [KB+M / Gamepad / Touch]
- **Session Type**: [First time / Returning / Targeted test]

## Test Focus
[What specific features or flows were being tested]

## First Impressions (First 5 minutes)
- **Understood the goal?** [Yes/No/Partially]
- **Understood the controls?** [Yes/No/Partially]
- **Emotional response**: [Engaged/Confused/Bored/Frustrated/Excited]
- **Notes**: [Observations]

## Gameplay Flow
### What worked well
- [Observation 1]

### Pain points
- [Issue 1 -- Severity: High/Medium/Low]

### Confusion points
- [Where the player was confused and why]

### Moments of delight
- [What surprised or pleased the player]

## Bugs Encountered
| # | Description | Severity | Reproducible |
|---|-------------|----------|-------------|

## Feature-Specific Feedback
### [Feature 1]
- **Understood purpose?** [Yes/No]
- **Found engaging?** [Yes/No]
- **Suggestions**: [Tester suggestions]

## Quantitative Data (if available)
- **Deaths**: [Count and locations]
- **Time per area**: [Breakdown]
- **Items used**: [What and when]
- **Features discovered vs missed**: [List]

## Overall Assessment
- **Would play again?** [Yes/No/Maybe]
- **Difficulty**: [Too Easy / Just Right / Too Hard]
- **Pacing**: [Too Slow / Good / Too Fast]
- **Session length preference**: [Shorter / Good / Longer]

## Top 3 Priorities from this session
1. [Most important finding]
2. [Second priority]
3. [Third priority]
```

In `new` mode, stop here with: Verdict: **COMPLETE** — blank template output; nothing saved.

---

## Phase 2B: Analyze Mode

Read the raw notes at the provided path. Cross-reference with existing design documents, reading each by section: find the headings you need with the Grep tool (pattern `^#`, content mode) and Read those ranges with offset and limit. Fill in the template above with structured findings. Flag any playtest observations that conflict with design intent.

An observation that describes a defect — a crash, a framerate drop, a softlock,
something that plainly breaks rather than plays badly — goes in the **Bugs
Encountered** table, not under Gameplay Flow → Pain points, and is routed as a
bug in Phase 3. Pain points are for how the game feels to play.

---

## Phase 3: Action Routing

Categorize all findings into four buckets:

- **Design changes needed** — fun issues, player confusion, broken mechanics, observations that conflict with the GDD's intended experience
- **Balance adjustments** — numbers feel wrong, difficulty too spiked or too flat
- **Bug reports** — clear implementation defects that are reproducible
- **Polish items** — not blocking progress, but friction or feel issues for later

Present the categorized list, then route:

- **Design changes:** "Run `$ccgs-propagate-design-change [path]` on the affected design document to find downstream impacts before making changes."
- **Balance adjustments:** "Run `$ccgs-balance-check [system]` to verify the full balance picture before tuning values."
- **Bugs:** "Use `$ccgs-bug-report` to formally track these."
- **Polish items:** "Add to the polish backlog in `production/` when the team reaches that phase."

---

## Phase 3b: Creative Director Player Experience Review

**Review mode check** — apply before spawning CD-PLAYTEST:
- `solo` → skip. Note: "CD-PLAYTEST skipped — Solo mode." Proceed to Phase 4 (save the report).
- `lean` → skip (not a PHASE-GATE). Note: "CD-PLAYTEST skipped — Lean mode." Proceed to Phase 4 (save the report).
- `full` → spawn as normal.

After categorising findings, spawn `ccgs-creative-director` via
`native delegation` using gate **CD-PLAYTEST** (`.agents/studio/docs/director-gates/cd-playtest.md`).

Pass: the structured report content, game pillars and core fantasy (from
`design/gdd/game-concept.md`), the specific hypothesis being tested. **If
`game-concept.md` does not exist** — expected at `minimal`, where
`design/game-brief.md` replaces it — the brief has no pillars: pass its
one-sentence pitch and its "Who it's for / what they feel" line instead, and say
they stand in for pillars. If neither document exists, say so in the prompt:
*"No pillars available — assess against the hypothesis alone."* A director gate
handed silence about pillars will invent them.

Present the creative director's assessment before saving the report. If CONCERNS or REJECT, add a `## Creative Director Assessment` section to the report capturing the verdict and feedback. If APPROVE, note the approval in the report. If NOT ASSESSED (the director lacked an input — `.agents/studio/docs/director-gates.md`), add the same section naming what was missing; it is not an approval.

---

## Phase 4: Save Report

Write this within the accepted playtest-report scope to
`production/qa/playtests/playtest-[date]-[tester].md`, creating the directory if
needed; do not ask for a second file-creation approval.

---

## Phase 5: Next Steps

Verdict: **COMPLETE** — playtest report generated.

- Act on the highest-priority finding category first.
- After addressing design changes: re-run `$ccgs-design-review` on the updated GDD.
- After fixing bugs: re-run `$ccgs-bug-triage` to update priorities.
