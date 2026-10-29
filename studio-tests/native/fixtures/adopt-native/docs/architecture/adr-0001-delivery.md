# ADR-0001: Delivery ownership

## Status
Accepted
## ADR Dependencies
None.
## Engine Compatibility
Godot 4.6.1, GDScript.
## GDD Requirements Addressed
- TR-DELIVERY-001
## Performance Implications
No per-frame allocations in delivery checks.
## Decision
DeliveryService owns parcel state and emits delivery-recorded.
