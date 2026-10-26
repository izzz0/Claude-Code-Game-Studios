Epic: Courier Core
Status: Incomplete
Layer: Gameplay
Type: Logic
Estimate: S
Manifest Version: 2026-10-26

# Story 001: Move through wall boundaries

## Context

GDD: design/game-brief.md — movement MVP.
TR-courier-001: not registered; minimal workflow uses the brief.
ADR Governing Implementation: N/A (minimal — no architecture decision required)
Engine/Risk: Godot 4.6.1 / NOT ASSESSED until runtime verification.
Engine Notes: Plain GDScript movement only.
Control Manifest Rules: N/A — manifest not yet created.

## Acceptance Criteria

- [ ] AC-1: A/D movement changes the courier's horizontal position.
- [ ] AC-2: Wall boundaries prevent movement outside the play area.
- [ ] AC-3: The movement boundary test is retained.

## Implementation Notes

Movement is not complete, so dependent collection work must wait.

## Out of Scope

Target collection and restart.

## Files

src/courier.gd

## Test Evidence

tests/unit/courier/movement-wall_test.gd

## Dependencies

None.
