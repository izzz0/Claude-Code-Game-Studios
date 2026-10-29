# Engine and code root

Resolve engine.name, engine.language and the explicit code root through yaml-helper.sh. An unset engine must be configured before engine-code implementation. Default roots are Godot src/, Unity Assets/, Unreal Source/; an explicitly configured valid custom root is preserved.

Use the actual project root for config and the shared resource root for helper paths. Nested projects keep their own nearest configuration. Starting from a subdirectory, a Git worktree, a Unicode path or a path with spaces must not target another project.

Specialist settings may use original role names; route known names to ccgs-native profiles without rewriting user config. null/empty is unset. Missing profiles/toolchains are NOT ASSESSED, never assumed to have run.
