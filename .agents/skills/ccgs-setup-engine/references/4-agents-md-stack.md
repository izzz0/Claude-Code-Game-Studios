# $ccgs-setup-engine — Section 4: Confirm Project Technology Stack

> Part of `$ccgs-setup-engine`. `SKILL.md` names when to read this file; the settings it
> resolved and the rules under its later headings still apply here.

## 4. Confirm Project Technology Stack

### Language Selection (Godot only)

If Godot was chosen and the language is still unset, ask which language to use before showing the proposed Technology Stack. Preserve an already confirmed language.

> "Godot supports two primary languages:
>
>   **A) GDScript** — Python-like, Godot-native, fastest iteration. Best for beginners, solo devs, and teams coming from Python or Lua.
>   **B) C#** — .NET 8+, familiar to Unity developers, stronger IDE tooling (Rider / Visual Studio), slight performance advantage on heavy logic.
>   **C) Both** — GDScript for gameplay/UI scripting, C# for performance-critical systems. Advanced setup — requires .NET SDK alongside Godot.
>
> Which will this project primarily use?"

Record the choice in project configuration and technical preferences. It determines naming conventions, specialist routing, and which agent is spawned for code files throughout the project.

### Primary Language (Unreal)

If Unreal was chosen, ask via
`native user-input mechanism`: "Will most gameplay logic live in
C++ or in Blueprints?" — `[A] C++ (Blueprints for tuning and prototyping)` /
`[B] Blueprint-primary (C++ only where needed)`. Default to C++ if the user has no
preference. The answer sets `engine.language` (`"C++"` or `"Blueprint"`).

---

Read the applicable `AGENTS.md` instructions and check them against the confirmed
engine choices. The shipped studio rules already route through `project.yaml`
and the matching engine reference, so ordinary engine selection does not require
rewriting instruction files. Store mutable technology values in `project.yaml`
and `docs/technical-preferences.md` instead. Preserve existing project rules and
ask about an actual conflict or a necessary instruction change. If the host
requires human review of such a change, retain the blocker; do not approve it or
use another tool to write a protected instruction path.

Use these technology values in the project-owned preferences, replacing any
applicable `[CHOOSE]` placeholders:

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

Read the chosen engine's version reference before using engine APIs, following
the existing dynamic routing rule. Record the selected reference in the
project-owned preferences. Existing `ENGINE-REFERENCE-IMPORT` markers are legacy
instructions to inspect for conflicts, not a reason to rewrite `AGENTS.md` on
every setup:
- Godot → read `docs/engine-reference/godot/VERSION.md`
- Unity → read `docs/engine-reference/unity/VERSION.md`
- Unreal → read `docs/engine-reference/unreal/VERSION.md`
- Cocos → read `docs/engine-reference/Cocos/VERSION.md`

This keeps the next session from reading another engine's reference.
It is idempotent — re-running `$ccgs-setup-engine` updates only changed project
values. (The target `docs/engine-reference/<engine>/`
directory is created in Section 7, Populate Engine Reference Docs, if it does not yet exist.)

---
