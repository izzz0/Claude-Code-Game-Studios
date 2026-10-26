---
name: ccgs-setup-engine
description: Select, verify, pin, and scaffold Godot, Unity, Unreal or Cocos Creator projects using actual installed tooling.
---

# Engine setup

Read `.agents/studio/docs/core-workflow.md`, resolve the root, then read `docs/engine-reference/<engine>/VERSION.md` and only relevant module references.

## Inputs

Existing `project.yaml`, engine project files, official documentation/version, and the user's requested engine/platform/language.

## Actions

- Resolve first with `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,engine_values`; preserve an existing engine/version/path/language.
- Discover the installed editor/version, existing project and useful commands first. On Windows, use the repository runtime's `context.bash_executable()` resolution (Git Bash/POSIX Bash) for discovery; do not edit global PATH or hardcode a machine-specific path. Ask about the engine, target platform or language only when the choice is missing and consequential; derive technical commands from the project/tooling instead of requiring the user to design them. Pin name/version/language/path and applicable commands with config-set.sh <key> <value> --dry-run, then the authorized write.
- Keep code roots `src/`, `Assets/`, and `Source/` for Godot, Unity and Unreal. For Cocos Creator 3.8.8, use `resolve_code_roots` for actual client/shared/protocol/server TypeScript directories and read `docs/engine-reference/Cocos/`. Never infer an engine merely from a directory name; generated shared trees remain read-only.
- Verify executable/version and official docs. Godot may create `project.godot` and a tiny launchable scene; Unity/Unreal must be scaffolded by installed tooling, never fabricated.
- For Cocos, preserve the existing Creator build/preview scripts, pin TypeScript and the installed Creator version, and derive Node test and build commands from the actual project. Verify raw Creator success semantics, fresh Web entry and real launch separately; no guessed build success or runtime pass.
- Initialize stage only when absent, using `bash .agents/studio/scripts/set-stage.sh <Stage>`; preserve an existing stage. Report `scaffold`, `engine.path`, `engine.name/version/language`, all code roots, and actual commands.

## Output

Return the pinned setup and verification result. If the editor is unavailable, setup may be recorded but implementation/runtime remains blocked; route to `ccgs-brainstorm` or `ccgs-create-stories` only when the design is ready.

## Standard/full workflow

Resolve workflow with the command above. For standard or full, read references/full-workflow.md and apply its artifact, review, and evidence phases, subject to .agents/studio/docs/core-workflow.md; minimal remains the default and stops at the minimal contract.
