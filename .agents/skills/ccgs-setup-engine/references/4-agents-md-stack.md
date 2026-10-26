# $ccgs-setup-engine — Section 4: Update AGENTS.md Technology Stack

> Part of `$ccgs-setup-engine`. `SKILL.md` names when to read this file; the settings it
> resolved and the rules under its later headings still apply here.

## 4. Update AGENTS.md Technology Stack

### Language Selection (Godot only)

If Godot was chosen, ask the user which language to use **before** showing the proposed Technology Stack:

> "Godot supports two primary languages:
>
>   **A) GDScript** — Python-like, Godot-native, fastest iteration. Best for beginners, solo devs, and teams coming from Python or Lua.
>   **B) C#** — .NET 8+, familiar to Unity developers, stronger IDE tooling (Rider / Visual Studio), slight performance advantage on heavy logic.
>   **C) Both** — GDScript for gameplay/UI scripting, C# for performance-critical systems. Advanced setup — requires .NET SDK alongside Godot.
>
> Which will this project primarily use?"

Record the choice. It determines the AGENTS.md template, naming conventions, specialist routing, and which agent is spawned for code files throughout the project.

### Primary Language (Unreal)

If Unreal was chosen, ask via
`native user-input mechanism`: "Will most gameplay logic live in
C++ or in Blueprints?" — `[A] C++ (Blueprints for tuning and prototyping)` /
`[B] Blueprint-primary (C++ only where needed)`. Default to C++ if the user has no
preference. The answer sets `engine.language` (`"C++"` or `"Blueprint"`).

---

Read `AGENTS.md` and update its Technology Stack from the engine choices already
confirmed for this setup. Preserve other project instructions. Ask only if the
existing stack conflicts with those choices; ordinary authorized synchronization
does not require another file permission prompt.

Update the Technology Stack section, replacing the `[CHOOSE]` placeholders with the actual values:

**For Godot** — use the template matching the language chosen above. See `references/godot-language-config.md` (**A1**) for all three variants (GDScript, C#, Both).

**For Unity:**
```markdown
- **Engine**: Unity [version]
- **Language**: C#
- **Build System**: Unity Build Pipeline
- **Asset Pipeline**: Unity Asset Import Pipeline + Addressables
```

**For Unreal:**
```markdown
- **Engine**: Unreal Engine [version]
- **Language**: [C++ (primary), Blueprint (gameplay prototyping) | Blueprint (primary), C++ where needed]
- **Build System**: Unreal Build Tool (UBT)
- **Asset Pipeline**: Unreal Content Pipeline
```
The Language line follows the primary-language answer above: the first form for
`[A]` (`engine.language: "C++"`), the second for `[B]` (`"Blueprint"`).

### Explicit engine reference instruction

In the same AGENTS.md update, set an explicit instruction to read the chosen
engine's version reference before using engine APIs. Keep the legacy
`ENGINE-REFERENCE-IMPORT` marker for an idempotent update, but use plain Codex
instructions rather than an automatic-import syntax:
- Godot → read `docs/engine-reference/godot/VERSION.md`
- Unity → read `docs/engine-reference/unity/VERSION.md`
- Unreal → read `docs/engine-reference/unreal/VERSION.md`
- Cocos → read `docs/engine-reference/Cocos/VERSION.md`

This keeps the next session from reading another engine's reference.
It is idempotent — re-running `$ccgs-setup-engine` for a different
engine rewrites the same line. (The target `docs/engine-reference/<engine>/`
directory is created in Section 7, Populate Engine Reference Docs, if it does not yet exist.)

---
