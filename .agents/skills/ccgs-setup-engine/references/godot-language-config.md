# Godot Language Configuration — setup-engine reference

Lookup tables for `$ccgs-setup-engine`, split out of the skill body so they cost
nothing on invocations that are not Godot. Read this file only when the
chosen engine is Godot, and then only the subsection for the chosen language.

Referenced from Sections 4, 5 and 5.5 of `$ccgs-setup-engine` by the names A1, A2
and A3.

**In this file:**

- A1. AGENTS.md Technology Stack Templates
- A2. Naming Conventions
- A3. Engine Specialists Routing

---

### A1. AGENTS.md Technology Stack Templates

**GDScript:**
```markdown
- **Engine**: Godot [version]
- **Language**: GDScript
- **Build System**: SCons (engine), Godot Export Templates
- **Asset Pipeline**: Godot Import System + custom resource pipeline
```

> **Guardrail**: When using this GDScript template, write the Language field as exactly "`GDScript`" — no additions. Do NOT append "C++ via GDExtension" or any other language. The C# template below includes GDExtension because C# projects commonly wrap native code; GDScript projects do not.

**C#:**
```markdown
- **Engine**: Godot [version]
- **Language**: C# (.NET 8+, primary), C++ via GDExtension (native plugins only)
- **Build System**: .NET SDK + Godot Export Templates
- **Asset Pipeline**: Godot Import System + custom resource pipeline
```

**Both — GDScript + C#:**
```markdown
- **Engine**: Godot [version]
- **Language**: GDScript (gameplay/UI scripting), C# (performance-critical systems), C++ via GDExtension (native only)
- **Build System**: .NET SDK + Godot Export Templates
- **Asset Pipeline**: Godot Import System + custom resource pipeline
```

---

### A2. Naming Conventions

**GDScript:**
- Classes: PascalCase (e.g., `PlayerController`)
- Variables/functions: snake_case (e.g., `move_speed`)
- Signals: snake_case past tense (e.g., `health_changed`)
- Files: snake_case matching class (e.g., `player_controller.gd`)
- Scenes: snake_case matching the file (e.g., `player_controller.tscn`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_HEALTH`)

> **This list and the
aming` enum table in Section 5.5.1 of the skill must
> agree, value for value.** They are written into two different files —
> `technical-preferences.md` from here, `project.yaml` from there — and Section
> 5.5.3 compares them and **stops the skill** on any mismatch.

**C#:**
- Classes: PascalCase (`PlayerController`) — must also be `partial`
- Public properties/fields: PascalCase (`MoveSpeed`, `JumpVelocity`)
- Private fields: `_camelCase` (`_currentHealth`, `_isGrounded`)
- Methods: PascalCase (`TakeDamage()`, `GetCurrentHealth()`)
- Signal delegates: PascalCase + `EventHandler` suffix (`HealthChangedEventHandler`)
- Files: PascalCase matching class (`PlayerController.cs`)
- Scenes: PascalCase matching root node (`PlayerController.tscn`)
- Constants: PascalCase (`MaxHealth`, `DefaultMoveSpeed`)

**Both — GDScript + C#:**
Use GDScript conventions for `.gd` files and C# conventions for `.cs` files.
The language boundary is per file. Resolve an unclear system language with the
user and record the choice in `technical-preferences.md`.

---

### A3. Engine Specialists Routing

**GDScript:**
```markdown
## Engine Specialists
- **Primary**: ccgs-godot-specialist
- **Language/Code Specialist**: ccgs-godot-gdscript-specialist (all .gd files)
- **Shader Specialist**: ccgs-godot-shader-specialist (.gdshader files, VisualShader resources)
- **UI Specialist**: ccgs-godot-specialist (no dedicated UI specialist — primary covers all UI)
- **Additional Specialists**: ccgs-godot-gdextension-specialist (GDExtension / native C++ bindings only)
- **Routing Notes**: Invoke primary for architecture decisions, ADR validation, and cross-cutting code review. Invoke GDScript specialist for code quality, signal architecture, static typing enforcement, and GDScript idioms. Invoke shader specialist for material design and shader code. Invoke GDExtension specialist only when native extensions are involved.

### File Extension Routing

| File Extension / Type | Specialist to Spawn |
|-----------------------|---------------------|
| Game code (.gd files) | ccgs-godot-gdscript-specialist |
| Shader / material files (.gdshader, VisualShader) | ccgs-godot-shader-specialist |
| UI / screen files (Control nodes, CanvasLayer) | ccgs-godot-specialist |
| Scene / prefab / level files (.tscn, .tres) | ccgs-godot-specialist |
| Native extension / plugin files (.gdextension, C++) | ccgs-godot-gdextension-specialist |
| General architecture review | ccgs-godot-specialist |
```

**C#:**
```markdown
## Engine Specialists
- **Primary**: ccgs-godot-specialist
- **Language/Code Specialist**: ccgs-godot-csharp-specialist (all .cs files)
- **Shader Specialist**: ccgs-godot-shader-specialist (.gdshader files, VisualShader resources)
- **UI Specialist**: ccgs-godot-specialist (no dedicated UI specialist — primary covers all UI)
- **Additional Specialists**: ccgs-godot-gdextension-specialist (GDExtension / native C++ bindings only)
- **Routing Notes**: Invoke primary for architecture decisions, ADR validation, and cross-cutting code review. Invoke C# specialist for code quality, [Signal] delegate patterns, [Export] attributes, .csproj management, and C#-specific Godot idioms. Invoke shader specialist for material design and shader code. Invoke GDExtension specialist only when native C++ plugins are involved.

### File Extension Routing

| File Extension / Type | Specialist to Spawn |
|-----------------------|---------------------|
| Game code (.cs files) | ccgs-godot-csharp-specialist |
| Shader / material files (.gdshader, VisualShader) | ccgs-godot-shader-specialist |
| UI / screen files (Control nodes, CanvasLayer) | ccgs-godot-specialist |
| Scene / prefab / level files (.tscn, .tres) | ccgs-godot-specialist |
| Project config (.csproj, NuGet) | ccgs-godot-csharp-specialist |
| Native extension / plugin files (.gdextension, C++) | ccgs-godot-gdextension-specialist |
| General architecture review | ccgs-godot-specialist |
```

**Both — GDScript + C#:**
```markdown
## Engine Specialists
- **Primary**: ccgs-godot-specialist
- **GDScript Specialist**: ccgs-godot-gdscript-specialist (.gd files — gameplay/UI scripts)
- **C# Specialist**: ccgs-godot-csharp-specialist (.cs files — performance-critical systems)
- **Shader Specialist**: ccgs-godot-shader-specialist (.gdshader files, VisualShader resources)
- **UI Specialist**: ccgs-godot-specialist (no dedicated UI specialist — primary covers all UI)
- **Additional Specialists**: ccgs-godot-gdextension-specialist (GDExtension / native C++ bindings only)
- **Routing Notes**: Invoke primary for cross-language architecture decisions and which systems belong in which language. Invoke GDScript specialist for .gd files. Invoke C# specialist for .cs files and .csproj management. Prefer signals over direct cross-language method calls at the boundary.

### File Extension Routing

| File Extension / Type | Specialist to Spawn |
|-----------------------|---------------------|
| Game code (.gd files) | ccgs-godot-gdscript-specialist |
| Game code (.cs files) | ccgs-godot-csharp-specialist |
| Cross-language boundary decisions | ccgs-godot-specialist |
| Shader / material files (.gdshader, VisualShader) | ccgs-godot-shader-specialist |
| UI / screen files (Control nodes, CanvasLayer) | ccgs-godot-specialist |
| Scene / prefab / level files (.tscn, .tres) | ccgs-godot-specialist |
| Project config (.csproj, NuGet) | ccgs-godot-csharp-specialist |
| Native extension / plugin files (.gdextension, C++) | ccgs-godot-gdextension-specialist |
| General architecture review | ccgs-godot-specialist |
```
