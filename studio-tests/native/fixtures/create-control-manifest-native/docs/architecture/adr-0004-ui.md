# ADR-0004: HUD read model
## Status
Accepted
## Decision
HUD always consumes delivery events and never mutates delivery state.
## Alternatives Considered
HUD mutation rejected as an ownership leak.
## Engine Compatibility
Godot 4.6.1 Control nodes.
## Performance Implications
Update labels only on signal receipt.
