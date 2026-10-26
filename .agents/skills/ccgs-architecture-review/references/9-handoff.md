# $ccgs-architecture-review — Phase 9: Handoff

> Part of `$ccgs-architecture-review`. `SKILL.md` names when to read this file; the settings it
> resolved and the rules under its later headings still apply here.

## Phase 9: Handoff

After completing the review and writing approved files, present:

1. **Immediate actions**: List the top 3 ADRs to create (highest-impact gaps first,
   Foundation layer before Feature layer)
2. **Pre-gate checklist**: Check whether these exist via Glob and mark each ✅ or ❌:
   - the engine's test root — `tests/unit/` and `tests/integration/` (Godot), `Assets/Tests/EditMode/` and `Assets/Tests/PlayMode/` (Unity), `Source/<Module>/Private/Tests/` (Unreal) — if ❌: run `$ccgs-test-setup`
   - `.github/workflows/tests.yml` — if ❌: run `$ccgs-test-setup`
   - `design/accessibility-requirements.md` — if ❌: run `$ccgs-ux-design`
   - `design/ux/interaction-patterns.md` — if ❌: run `$ccgs-ux-design`
   Present ❌ items as required steps before gate-check. Do not offer `$ccgs-gate-check`
   as an option if any item is ❌ — offer the missing skill to run instead.
3. **Rerun trigger**: "Re-run `$ccgs-architecture-review` after each new ADR is written
   to verify coverage improves"

Then close with
`native user-input mechanism` tailored to the pre-gate checklist state:
- If ADR gaps remain or any pre-gate item is ❌:
  - "Architecture review complete. What would you like to do next?"
    - [A] Write a missing ADR — start a new independent Codex run and run `$ccgs-architecture-decision [system]`
    - [B] Run `$ccgs-test-setup` — required before gate-check (only show if test infrastructure is ❌)
    - [C] Run `$ccgs-ux-design` — required before gate-check (only show if UX/accessibility files are ❌)
    - [D] Stop here for this session
- If all pre-gate checklist items are ✅ and no blocking ADR gaps remain:
  - "Architecture review complete. All pre-gate items confirmed. What would you like to do next?"
    - [A] Run `$ccgs-gate-check pre-production`
    - [B] Write a missing ADR — start a new independent Codex run and run `$ccgs-architecture-decision [system]`
    - [C] Stop here for this session

---
