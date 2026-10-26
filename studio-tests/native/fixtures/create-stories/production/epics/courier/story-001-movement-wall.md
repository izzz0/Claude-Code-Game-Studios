Epic: Courier Core
Status: Ready
Layer: Gameplay
Type: Logic
Estimate: S
Manifest Version: 2026-10-26

# Story 001: Move through wall boundaries

## Context

GDD: design/game-brief.md — MVP feature: keyboard movement with wall boundaries.
TR-courier-001: not registered; minimal workflow uses the brief.
ADR Governing Implementation: N/A (minimal — no architecture decision required)
Engine/Risk: Godot 4.6.1 / NOT ASSESSED until runtime verification.
Engine Notes: Use plain GDScript movement and a bounded position; no post-cutoff API.
Control Manifest Rules: N/A — manifest not yet created.

## Acceptance Criteria

- [ ] AC-1: Pressing A or D changes the courier's horizontal position within the configured movement bounds.
- [ ] AC-2: The courier cannot move past either wall boundary when movement input is held.
- [ ] AC-3: A Logic test records both an in-bounds movement and a blocked wall-boundary attempt.

## Implementation Notes

Keep movement independent from target collection so Story 002 can depend on this stable boundary behavior.

## Out of Scope

Target collection, restart flow, art, audio, and online services.

## Files

To be replaced by `$ccgs-dev-story` with the actual implementation files.

## Test Evidence

tests/unit/courier/movement-wall_test.gd

## Dependencies

None.
