# Courier System

> **Status**: Approved

## Overview
The courier delivers three parcels through a bounded harbor lane.
## Player Fantasy
Make a precise, calm delivery run under time pressure.
## Detailed Rules
Horizontal input moves the courier; each parcel can be delivered once.
## Formulas
score = delivered_parcels * 100 - elapsed_seconds
## Edge Cases
A wall blocks movement and duplicate parcel contact is ignored.
## Dependencies
Movement precedes delivery; the HUD reads delivery count.
## Tuning Knobs
move_speed = 180; delivery_count = 3.
## Acceptance Criteria
- Three distinct parcels produce completion exactly once.
