# Delivery System
## Overview
Records the courier's three parcel deliveries.
## Player Fantasy
Be reliable under a visible countdown.
## Detailed Design
Each parcel is claimed once and the third claim completes the run.
## Formulas
score = delivered * 100 - elapsed_seconds; delivered ∈ {0,1,2,3}.
## Edge Cases
Duplicate contact is idempotent; leaving the lane does not reset progress.
## Dependencies
Movement uses design/gdd/movement.md; HUD uses design/gdd/hud.md.
## Tuning Knobs
delivery_count = 3; completion_bonus = 100.
## Acceptance Criteria
- AC-1: three unique parcels produce completion.
- AC-2: duplicate contact leaves count unchanged.
- AC-3: score uses the documented formula.
