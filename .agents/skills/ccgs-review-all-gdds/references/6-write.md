# $ccgs-review-all-gdds — Phase 6: Read-only Report Handoff

Return the report and proposed tracking changes in the response. Do not write
GDDs, systems-index.md, review logs, QA evidence or execution checkpoints during
this review. The authorized coordinator may retain returned findings afterwards.

The proposed report path is `design/gdd/gdd-cross-review-[YYYY-MM-DD].md`.
Use an ISO date if the coordinator saves it: `review-scope.sh` orders prior
reports lexically, so other date orders can select the wrong baseline.

For each flagged GDD, propose the exact `Needs Revision` systems-index status
without parenthetical additions. Include current input hashes so the coordinator
can re-read and reconcile concurrent changes before applying anything.

Return a session summary containing verdict, N of M GDDs actually reviewed,
phases not run, flagged documents, blockers and recommended next action. State
that it is returned, not saved; do not claim the checkpoint was updated.

PASS can proceed. CONCERNS requires explicit acceptance of the listed risks.
FAIL and NOT ASSESSED retain the stage; missing inputs or required independent
review cannot be replaced by a document merely existing.
