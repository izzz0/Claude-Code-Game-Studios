# Test Evidence: Deliver a parcel

Story: `production/epics/courier/story-001-delivery.md`
Story Type: Logic
Tester: Native QA profile

## Acceptance Criteria Results

| AC-1 | PASS | index 0 |
| AC-2 | PASS | index 1 |
| AC-3 | FAIL | index 2 is rejected by delivery.gd |

## Observations

The source has an off-by-one guard: collection stops at 2 instead of allowing
the third target. This is a blocking finding requiring two/three target review.
