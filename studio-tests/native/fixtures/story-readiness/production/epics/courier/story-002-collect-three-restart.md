Epic: Courier Core
Status: Ready
Layer: Gameplay
Type: Integration
Estimate: M
Manifest Version: 2026-10-26

# Story 002: Collect three targets and restart

## Context

GDD: design/game-brief.md — second MVP feature, after movement.
TR-courier-002: not registered; minimal workflow uses the brief.
ADR Governing Implementation: N/A (minimal — no architecture decision required)
Engine/Risk: Godot 4.6.1 / NOT ASSESSED until runtime verification.
Engine Notes: Use existing movement boundary behavior; no post-cutoff API.
Control Manifest Rules: N/A — manifest not yet created.

## Acceptance Criteria

- [ ] AC-1: Reaching each of three distinct targets records exactly one collection.
- [ ] AC-2: After the third target is collected, restarting clears the collection state and starts a new run.
- [ ] AC-3: Duplicate contact with a collected target does not increase the collection count.

## Implementation Notes

The movement story must be complete before this integration behavior is implemented.

## Out of Scope

New movement rules, art, audio, and online persistence.

## Files

src/targets.gd

## Test Evidence

production/qa/playtests/story-002-collect-three-restart.md

## Dependencies

Story 001: Move through wall boundaries.
