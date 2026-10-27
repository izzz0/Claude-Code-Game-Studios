# ADR-0002: Delivery state
## Status
Accepted
## Decision
DeliveryService must own parcel state and emit delivery-recorded.
## Alternatives Considered
HUD ownership rejected because presentation must remain read-only.
## Engine Compatibility
Godot 4.6.1 signals.
## Performance Implications
One signal per accepted parcel.
