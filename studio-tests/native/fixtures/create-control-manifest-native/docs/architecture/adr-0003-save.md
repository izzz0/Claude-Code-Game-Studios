# ADR-0003: Save boundary
## Status
Accepted
## Decision
SaveService must persist the completed delivery count between scenes.
## Alternatives Considered
Scene-local state rejected because it loses completion.
## Engine Compatibility
Godot 4.6.1 ConfigFile.
## Performance Implications
Write only on completion.
