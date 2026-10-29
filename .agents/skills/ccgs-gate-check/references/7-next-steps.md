# $ccgs-gate-check — Sections 7 and 8: Next Step and Follow-Up

> Part of `$ccgs-gate-check`. `SKILL.md` names when to read this file; the settings it
> resolved and the rules under its later headings still apply here.

## 7. Closing Next-Step Widget

**In this file:**

- 7. Closing Next-Step Widget: per gate, and the `workflow: minimal` route
- 8. Follow-Up Actions

After the verdict is presented and any stage update is complete (project.yaml + stage.txt), close with a structured next-step prompt using `the caller's input channel`.

**Tailor the options to the gate that just ran.** The argument names the phase
being entered, so `$ccgs-gate-check systems-design` is the Concept → Systems Design gate.

**At `workflow: minimal`, skip the menus below.** They walk the phase ladder, and
the minimal route is not the ladder: offer the first incomplete step of
`paths.minimal` instead (the `--path minimal` rows from Section 3):
`$ccgs-setup-engine`, then `$ccgs-brainstorm` (or `$ccgs-reverse-document design [code root]`
when the code root already holds the game: it writes the brief from what is
built), then `$ccgs-create-stories`, then `$ccgs-dev-story` on the next story — the route
`$ccgs-help` gives.

For **Concept → Systems Design** (`$ccgs-gate-check systems-design`) PASS — option [A] is
`$ccgs-map-systems` when `design/gdd/systems-index.md` does not exist yet (many
projects write it during Concept, as the workflow catalog orders it), otherwise
`$ccgs-design-system [first system in the index's design order]`:
```
Gate passed. What would you like to do next?
[A] Run $ccgs-map-systems — decompose the concept into systems and a design order (recommended next step)
    — or, when the systems index already exists: Run $ccgs-design-system [first system] — author its GDD
[B] Revisit the concept first — return here when it is settled
[C] Stop here for this session
```

For **Systems Design → Technical Setup** (`$ccgs-gate-check technical-setup`) PASS:
```
Gate passed. What would you like to do next?
[A] Run $ccgs-create-architecture — produce your master architecture blueprint and ADR work plan (recommended next step)
[B] Design more GDDs first — return here when all MVP systems are complete
[C] Stop here for this session
```

> **Note for the Systems Design → Technical Setup PASS**: `$ccgs-create-architecture` is the required next step before writing any ADRs. It produces the master architecture document and a prioritized list of ADRs to write. Running `$ccgs-architecture-decision` without this step means writing ADRs without a blueprint — skip it at your own risk.

For **Technical Setup → Pre-Production** (`$ccgs-gate-check pre-production`) PASS:
```
Gate passed. What would you like to do next?
[A] Run $ccgs-create-control-manifest — generate the layer rules manifest from your Accepted ADRs (first, if docs/architecture/control-manifest.md does not exist yet)
[B] Run $ccgs-vertical-slice — build the Vertical Slice (do this before writing epics — validate fun first)
[C] Write more ADRs first — run $ccgs-architecture-decision [next-system]
[D] Stop here for this session
```

> **Note for the Technical Setup → Pre-Production PASS**: The Pre-Production sequence is deliberately ordered
> to validate fun before committing to detailed planning:
>
> 1. `$ccgs-create-control-manifest` — extract technical rules from Accepted ADRs, if not done yet (`$ccgs-create-epics` requires it at `full`)
> 2. `$ccgs-vertical-slice` — build the Vertical Slice **FIRST**, before writing epics or stories
> 3. Playtest → `$ccgs-playtest-report` — at least 1 documented session, 3+ better before committing the full team. `$ccgs-gate-check production` treats the slice as recommended: skipped → CONCERNS, unplayed → NOT ASSESSED
> 4. `$ccgs-ux-design [screen]` — UX specs for main menu, core HUD, pause menu (if not done)
> 5. `$ccgs-create-epics layer:foundation` then `$ccgs-create-epics layer:core` — plan after fun is validated
> 6. `$ccgs-create-stories [epic-slug]` for each epic
> 7. `$ccgs-sprint-plan new`
>
> **Why prototype before epics?** If the prototype reveals the core loop needs to change,
> epics written before that discovery will be partially wrong. Validate fun cheaply first,
> then plan in detail. This is the #1 lesson from GDC postmortem data.

For all other gates, offer the two most logical next steps for that phase plus "Stop here".

---

## 8. Follow-Up Actions

Based on the verdict, suggest specific next steps:

- **No art bible?** → `$ccgs-art-bible` to create the visual identity specification
- **Art bible exists but no asset specs?** → `$ccgs-asset-spec system:[name]` to generate per-asset visual specs and generation prompts from approved GDDs
- **No game concept?** → `$ccgs-brainstorm` to create one
- **No systems index?** → `$ccgs-map-systems` to decompose the concept into systems
- **Missing design docs?** → `$ccgs-reverse-document` or delegate to `ccgs-game-designer`
- **Small design change needed?** → `$ccgs-quick-design` for changes under about one week of implementation (bypasses full GDD pipeline)
- **No UX specs?** → `$ccgs-ux-design [screen name]` to author specs, or `$ccgs-team-ui [feature]` for full pipeline
- **UX specs not reviewed?** → `$ccgs-ux-review [file]` or `$ccgs-ux-review all` to validate
- **No accessibility requirements doc?** → `$ccgs-ux-design accessibility` to write `design/accessibility-requirements.md`
- **No interaction pattern library?** → `$ccgs-ux-design patterns` to initialize it
- **Concept or a GDD not reviewed?** → `$ccgs-design-review [doc]`
- **GDDs not cross-reviewed?** → `$ccgs-review-all-gdds` (run after all MVP GDDs are individually approved)
- **Cross-GDD consistency issues?** → fix flagged GDDs, then re-run `$ccgs-review-all-gdds`
- **No test framework?** → `$ccgs-test-setup` to scaffold the framework for your engine
- **No QA plan for current sprint?** → `$ccgs-qa-plan sprint` to generate one before implementation begins
- **Missing ADRs?** → `$ccgs-architecture-decision` for individual decisions
- **No master architecture doc?** → `$ccgs-create-architecture` for the full blueprint
- **ADRs missing engine compatibility sections?** → Re-run `$ccgs-architecture-decision`
  or manually add Engine Compatibility sections to existing ADRs
- **Missing control manifest?** → `$ccgs-create-control-manifest` (requires Accepted ADRs)
- **Missing epics?** → `$ccgs-create-epics layer: foundation` then `$ccgs-create-epics layer: core` (requires control manifest)
- **Missing stories for an epic?** → `$ccgs-create-stories [epic-slug]` (run after each epic is created)
- **Stories not implementation-ready?** → `$ccgs-story-readiness` to validate stories before developers pick them up
- **Tests failing?** → delegate to `ccgs-lead-programmer` or `ccgs-qa-tester`
- **No playtest data?** → `$ccgs-playtest-report`
- **No playtest sessions beyond the minimum?** → Additional sessions give more reliable signal. 3+ total is recommended before committing the full team. Use `$ccgs-playtest-report` to structure findings.
- **No Difficulty Curve doc?** → Author `design/difficulty-curve.md` by hand from the template at `.agents/studio/docs/templates/difficulty-curve.md`. (`$ccgs-quick-design` is a related session but writes to `design/quick-specs/`, not to this path — use it to think the curve through, then copy the outcome here.)
- **No player journey map?** → Author `design/player-journey.md` by hand from the template at `.agents/studio/docs/templates/player-journey.md`.

> **Neither of these has a skill that writes it — do not name one.**
> "`$ccgs-ux-design` Phase 2b" is the step that *reads* `design/player-journey.md`,
> so it lands the user back at the check that just failed. `$ccgs-quick-design`
> writes `design/quick-specs/[name]-[date].md` and leaves this gate still
> failing. Say plainly that both docs are hand-authored from their templates.
- **Need a quick sprint check?** → `$ccgs-sprint-status` for current sprint progress snapshot
- **Performance unknown?** → `$ccgs-perf-profile`
- **Not localized?** → `$ccgs-localize`
- **No security audit, or open CRITICAL/HIGH findings?** → `$ccgs-security-audit` (after fixes, `$ccgs-security-audit quick` to confirm)
- **Ready for release?** → `$ccgs-launch-checklist`

---
