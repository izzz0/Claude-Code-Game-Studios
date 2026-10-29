# ADR-0001: Godot input and boundary ownership

## Status

Accepted

## Requirements Addressed

- TR-MOVEMENT-001
- TR-COLLECTION-001

## Decision

The movement module owns GDScript input and wall collision; collection consumes its position contract.

## Consequences

The two MVP modules remain independently testable and the collection event has one owner.

## Engine Compatibility

Godot 4.6.1 and GDScript.
