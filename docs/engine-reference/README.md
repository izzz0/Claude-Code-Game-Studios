# Engine reference snapshots

These are inherited, version-specific starting points for Godot, Unity and
Unreal. They do not select or prove the engine installed for a new game.
The actual engine/version lives in project.yaml.

Use $ccgs-setup-engine to inspect the installation, select the version and record
official source URLs. Read that engine's VERSION.md and relevant module notes.
Verify mismatches or uncertain APIs against official docs for the chosen version;
do not assume a model's training cutoff or the snapshot's pin.

When upgrading, update the version record, affected module notes and source/
verification dates together. Preserve existing game decisions and report anything
not tested locally. Load engine-reference modules on demand.
