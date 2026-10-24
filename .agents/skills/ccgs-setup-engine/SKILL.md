---
name: ccgs-setup-engine
description: Select, verify, pin, and minimally scaffold a Godot, Unity, or Unreal project without fabricating unavailable engine projects.
---

# Engine setup

Read `.agents/studio/docs/core-workflow.md`, resolve the root, then read `docs/engine-reference/<engine>/VERSION.md` and only relevant module references.

## Inputs

Existing `project.yaml`, engine project files, official documentation/version, and the user's requested engine/platform/language.

## Actions

- Resolve first with `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,engine_values`; preserve an existing engine/version/path/language.
- Discover the installed editor/version, existing project and useful commands first. Ask about the engine, target platform or language only when the choice is missing and consequential; derive technical commands from the project/tooling instead of requiring the user to design them. Pin name/version/language/path and applicable commands with config-set.sh <key> <value> --dry-run, then the authorized write.
- Keep code roots `src/`, `Assets/`, and `Source/` respectively. Never infer Godot from `src/`.
- Verify executable/version and official docs. Godot may create `project.godot` and a tiny launchable scene; Unity/Unreal must be scaffolded by installed tooling, never fabricated.
- Record stage with `bash .agents/studio/scripts/set-stage.sh <Stage>`; report `scaffold`, `engine.path`, `engine.name/version/language`, code root, and commands.

## Output

Return the pinned setup and verification result. If the editor is unavailable, setup may be recorded but implementation/runtime remains blocked; route to `ccgs-brainstorm` or `ccgs-create-stories` only when the design is ready.
