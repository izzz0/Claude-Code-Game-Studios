# ADR-0001: Input boundary
## Status
Accepted
## Decision
MovementController always owns input mapping and wall collision.
## Alternatives Considered
Scene script ownership rejected because it couples UI and movement.
## Engine Compatibility
Godot 4.6.1 InputMap.
## Performance Implications
No allocations in the input path.
