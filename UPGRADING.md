# Migrating to the Codex core edition

This release replaces Claude-specific entrypoints with nine Codex skills.
Migrate on a branch and preserve your game's source, assets and local changes.
Use Git history to retrieve an original workflow that this release does not port.

Open the repository in Codex and use $ccgs-start. It inspects existing settings
and artifacts before proposing work. Do not overwrite project.yaml with the
template: its schema, explicit choices and personal override semantics remain.
Existing standard/full workflows are unsupported in this release; changing their
tier requires an explicit decision rather than automatic conversion.

Project instructions now use AGENTS.md. Shared framework resources live under
.agents/studio/. Scripts are invoked explicitly; the old permission rules,
status bar, agent hierarchy and automatic hooks have no Codex equivalent installed
by this migration. Review any custom helper paths and game launch commands.

There is no automatic upstream update checker. Review and merge future upstream
changes deliberately, accounting for the Codex-only structure.
