Epic: Health Rules
Status: Ready
Layer: Gameplay
Type: Logic
Estimate: S
Manifest Version: 2026-10-26

# Story 001: Clamp health to the valid range

## Context

GDD: design/game-brief.md — health clamp MVP.
TR-health-001: not registered; minimal workflow uses the brief.
ADR Governing Implementation: N/A (minimal — no architecture decision required)
Engine/Risk: Godot 4.6.1 / NOT ASSESSED until runtime verification.
Engine Notes: Pure GDScript function; no post-cutoff API.
Control Manifest Rules: N/A — manifest not yet created.

## Acceptance Criteria

- [ ] AC-1: `clamp_health(-5)` returns `0`.
- [ ] AC-2: `clamp_health(100)` returns `100`, and a value above 100 also returns `100`.
- [ ] AC-3: A genuine Godot unit test exercises both out-of-range boundaries and the in-range upper boundary.

## Implementation Notes

Keep the function pure and independent of scene state so it can be reused by later health UI work.

## Out of Scope

Scenes, UI, damage sources, healing effects, and fake test runners.

## Files

src/health.gd
tests/unit/health_test.gd

## Test Evidence

tests/unit/health_test.gd

## Dependencies

None.
