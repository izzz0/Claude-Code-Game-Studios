# $ccgs-setup-engine — Section 5: Populate Technical Preferences

> Part of `$ccgs-setup-engine`. `SKILL.md` names when to read this file; the settings it
> resolved and the rules under its later headings still apply here.

## 5. Populate Technical Preferences

**In this file:**

- Engine & Language Section
- Naming Conventions (engine defaults)
- Input & Platform Section
- Remaining Sections
- Engine Specialists Routing
- Collaborative Step

After checking the project rules, create or update the project's `docs/technical-preferences.md`
with engine-appropriate defaults. Read and preserve an existing project document.
If it is absent, initialize it from the read-only template at
`.agents/studio/docs/technical-preferences.md` only when that template exists;
never overwrite an existing project document or write the template path. For
each setting, prefer `project.yaml`; a blank or `[TO BE CONFIGURED]` value in
the project document leaves any configured legacy-template value available as
a per-key fallback. Fill in:

```bash
if [ ! -f docs/technical-preferences.md ] && [ -f .agents/studio/docs/technical-preferences.md ]; then
  mkdir -p docs
  cp .agents/studio/docs/technical-preferences.md docs/technical-preferences.md
fi
```

### Engine & Language Section
- Fill from the engine choice made in step 4

### Naming Conventions (engine defaults)

**For Godot** — see `references/godot-language-config.md` (**A2**) for GDScript, C#, and Both variants.

**For Unity (C#):**
- Classes: PascalCase (e.g., `PlayerController`)
- Public fields/properties: PascalCase (e.g., `MoveSpeed`)
- Private fields: _camelCase (e.g., `_moveSpeed`)
- Methods: PascalCase (e.g., `TakeDamage()`)
- Files: PascalCase matching class (e.g., `PlayerController.cs`)
- Constants: PascalCase or UPPER_SNAKE_CASE

**For Unreal (C++):**
- Classes: Prefixed PascalCase (`A` for Actor, `U` for UObject, `F` for struct)
- Variables: PascalCase (e.g., `MoveSpeed`)
- Functions: PascalCase (e.g., `TakeDamage()`)
- Booleans: `b` prefix (e.g., `bIsAlive`)
- Files: Match class without prefix (e.g., `PlayerController.h`)

### Input & Platform Section

Populate `## Input & Platform` using the answers gathered in Section 2 (or extracted
from the game concept). Derive the values using this mapping:

| Platform target | Gamepad Support | Touch Support |
|-----------------|-----------------|---------------|
| PC only | Partial (recommended) | None |
| Console | Full | None |
| Mobile | None | Full |
| PC + Console | Full | None |
| PC + Mobile | Partial | Full |
| Web | Partial | Partial |

For **Primary Input**, use the dominant input for the game genre:
- Action/RPG/platformer targeting console → Gamepad
- Strategy/point-and-click/RTS → Keyboard/Mouse
- Mobile game → Touch
- Cross-platform → ask the user

> **Genre may not exist yet — check before deriving from it.** At `minimal` the
> design artifact is `design/game-brief.md`, and it is authored *after* this
> skill runs (Section 2 says so explicitly). There is no genre to map. The same
> is true at any tier when `$ccgs-setup-engine` is run before the concept exists.
>
> When genre is unavailable, **ask** — do not infer one from the platform, and do
> not leave the field silently blank:
> - Prompt: "Primary input for a [2D/3D] [platform] game? Genre isn't established
>   yet — the brief comes next — so this can't be derived."
> - Options: the plausible inputs for that platform, plus
>   `Leave as [TO BE CONFIGURED]` — a legitimate answer here, revisited via
>   `$ccgs-settings` once the brief exists.
>
> Gamepad Support and Touch Support still come from the platform table above;
> only Primary Input depends on genre.

Present the derived values and ask the user to confirm or adjust before writing.

Example filled section:
```markdown
## Input & Platform
- **Target Platforms**: PC, Console
- **Input Methods**: Keyboard/Mouse, Gamepad
- **Primary Input**: Gamepad
- **Gamepad Support**: Full
- **Touch Support**: None
- **Platform Notes**: All UI must support d-pad navigation. No hover-only interactions.
```

### Remaining Sections
- **Performance Budgets**: Use
`native user-input mechanism`:
  - Prompt: "Should I set default performance budgets now, or leave them for later?"
  - Options: `[A] Set defaults now (60fps, 16.6ms frame budget, engine-appropriate draw call limit)` / `[B] Leave as [TO BE CONFIGURED] — I'll set these when I know my target hardware`
  - If [A]: populate with the suggested defaults. If [B]: leave as placeholder.
- **Testing**: Suggest the engine-appropriate framework — **gdUnit4** for Godot,
  NUnit for Unity, Automation Spec for Unreal — and ask before adding.
  > **Must match `commands.test` in Section 5.5.1, which writes gdUnit4's own
  > runner (`res://addons/gdUnit4/bin/GdUnitCmdTool.gd`), and
  > `.agents/studio/docs/coding-standards.md`, which names the same runner.** Naming GUT
  > here would have the skill recommend one framework and configure another in the
  > same run.
- **Forbidden Patterns**: Leave as placeholder — do NOT pre-populate.
- **Allowed Libraries**: Leave as placeholder — do NOT pre-populate dependencies the project does not currently need. Only add a library here when it is actively being integrated, not speculatively.

> **Guardrail**: Never add speculative dependencies to Allowed Libraries. For example, do NOT add GodotSteam unless Steam integration is actively beginning in this session. Post-launch integrations should be added to Allowed Libraries when that work begins, not during engine setup.

### Engine Specialists Routing

Also populate the `## Engine Specialists` section in `technical-preferences.md` with the correct routing for the chosen engine:

**For Godot** — see `references/godot-language-config.md` (**A3**) for the routing table matching the language chosen.

**For Unity:**
```markdown
## Engine Specialists
- **Primary**: ccgs-unity-specialist
- **Language/Code Specialist**: ccgs-unity-specialist (C# review — primary covers it)
- **Shader Specialist**: ccgs-unity-shader-specialist (Shader Graph, HLSL, URP/HDRP materials)
- **UI Specialist**: ccgs-unity-ui-specialist (UI Toolkit UXML/USS, UGUI Canvas, runtime UI)
- **Additional Specialists**: ccgs-unity-dots-specialist (ECS, Jobs system, Burst compiler), ccgs-unity-addressables-specialist (asset loading, memory management, content catalogs)
- **Routing Notes**: Invoke primary for architecture and general C# code review. Invoke DOTS specialist for any ECS/Jobs/Burst code. Invoke shader specialist for rendering and visual effects. Invoke UI specialist for all interface implementation. Invoke Addressables specialist for asset management systems.

### File Extension Routing

| File Extension / Type | Specialist to Spawn |
|-----------------------|---------------------|
| Game code (.cs files) | ccgs-unity-specialist |
| Shader / material files (.shader, .shadergraph, .mat) | ccgs-unity-shader-specialist |
| UI / screen files (.uxml, .uss, Canvas prefabs) | ccgs-unity-ui-specialist |
| Scene / prefab / level files (.unity, .prefab) | ccgs-unity-specialist |
| Native extension / plugin files (.dll, native plugins) | ccgs-unity-specialist |
| General architecture review | ccgs-unity-specialist |
```

**For Unreal:**
```markdown
## Engine Specialists
- **Primary**: ccgs-unreal-specialist
- **Language/Code Specialist**: ccgs-ue-blueprint-specialist (Blueprint graphs) or ccgs-unreal-specialist (C++)
- **Shader Specialist**: ccgs-unreal-specialist (no dedicated shader specialist — primary covers materials)
- **UI Specialist**: ccgs-ue-umg-specialist (UMG widgets, CommonUI, input routing, widget styling)
- **Additional Specialists**: ccgs-ue-gas-specialist (Gameplay Ability System, attributes, gameplay effects), ccgs-ue-replication-specialist (property replication, RPCs, client prediction, netcode)
- **Routing Notes**: Invoke primary for C++ architecture and broad engine decisions. Invoke Blueprint specialist for Blueprint graph architecture and BP/C++ boundary design. Invoke GAS specialist for all ability and attribute code. Invoke replication specialist for any multiplayer or networked systems. Invoke UMG specialist for all UI implementation.

### File Extension Routing

| File Extension / Type | Specialist to Spawn |
|-----------------------|---------------------|
| Game code (.cpp, .h files) | ccgs-unreal-specialist |
| Shader / material files (.usf, .ush, Material assets) | ccgs-unreal-specialist |
| UI / screen files (.umg, UMG Widget Blueprints) | ccgs-ue-umg-specialist |
| Scene / prefab / level files (.umap, .uasset) | ccgs-unreal-specialist |
| Native extension / plugin files (Plugin .uplugin, modules) | ccgs-unreal-specialist |
| Blueprint graphs (.uasset BP classes) | ccgs-ue-blueprint-specialist |
| General architecture review | ccgs-unreal-specialist |
```

### Collaborative Step
Present the filled-in preferences to the user. For Godot, include the chosen language and note where the full naming conventions and routing tables live:
Present the proposed values for `technical-preferences.md`. Resolve material
language, rendering, physics or platform choices with native user input; once
those choices are known, save the preferences as part of the authorized setup.

For all other engines, present the defaults directly without referencing the appendix.

Wait for approval before writing the file.

---
