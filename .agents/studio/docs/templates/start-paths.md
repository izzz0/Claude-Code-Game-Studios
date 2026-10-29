# Your Path

Here's your path at rigor `[value]`. Every skill still runs at any rigor; rigor changes
what's required, not what's allowed.

**`minimal`: 4 steps to running code**
1. `$ccgs-setup-engine`: choose and configure the engine
2. `$ccgs-brainstorm`: write the one-page `design/game-brief.md`
3. `$ccgs-create-stories`: turn the brief's MVP list into stories (no epics or sprint plan needed)
4. `$ccgs-dev-story`: the first line of game code

**`standard`**
- Concept: `$ccgs-setup-engine` → `$ccgs-brainstorm` → `$ccgs-prototype` → `$ccgs-art-bible` → `$ccgs-gate-check`
- Systems Design: `$ccgs-map-systems` → `$ccgs-design-system` (once per system) → `$ccgs-review-all-gdds` →
  `$ccgs-gate-check`
- Architecture: `$ccgs-create-architecture` → `$ccgs-architecture-decision` (once per decision) →
  `$ccgs-create-control-manifest` → `$ccgs-architecture-review` → `$ccgs-test-setup` → `$ccgs-ux-design`
  (accessibility and interaction patterns) → `$ccgs-gate-check`
- Pre-Production: `$ccgs-ux-design` (HUD and key screens) → `$ccgs-create-epics` → `$ccgs-create-stories` →
  `$ccgs-sprint-plan` → `$ccgs-gate-check`
- Production: `$ccgs-dev-story`

Each `$ccgs-gate-check` moves the project one stage, and only when it passes.

**`full`:** everything in `standard`, plus `$ccgs-vertical-slice` and `$ccgs-playtest-report` in
Pre-Production and `$ccgs-design-review` after each GDD.

**Path D with existing work** (stage `Systems Design` or later, or code on disk) gets this instead.
Print only the steps that apply, and for the brief only the one source that applies. At `minimal`:
1. `$ccgs-project-stage-detect`: what stage the project is at and what is missing
2. `$ccgs-adopt`: whether the existing files are in the format the skills read
3. `$ccgs-setup-engine`: only when no engine is set; leave it out when `engine` names one
4. The brief, only if `concept` is absent: `$ccgs-reverse-document design [code_root]` when the code
   root holds 10 or more source files (it writes the brief from the game), and then do not mention
   `$ccgs-brainstorm` at all; `$ccgs-brainstorm` only when it holds fewer

At `standard` and `full`, steps 1 to 3, then `$ccgs-design-system retrofit [path]`,
`$ccgs-architecture-decision retrofit [path]`, `$ccgs-architecture-review` and `$ccgs-gate-check`.

`minimal` is the documented floor, not a lesser mode. Its trade: no GDDs, so design
problems show up in code.
