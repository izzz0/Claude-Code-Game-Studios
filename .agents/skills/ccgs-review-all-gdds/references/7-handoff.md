# $ccgs-review-all-gdds — Phase 7: Handoff

> Part of `$ccgs-review-all-gdds`. `SKILL.md` names when to read this file; the settings it
> resolved and the rules under its later headings still apply here.

## Phase 7: Handoff

After returning the read-only report, recommend the next applicable action.
Use native user input only when a material choice remains unresolved.

Before building options, check project state:
- Are there any Warning-level items that are simple edits (flagged with "30-second edit", "brief addition", or similar)? → propose a separate authorized edit task
- Are any GDDs in the "Flagged for Revision" table? → offer $ccgs-design-review option for each
- Read systems-index.md for the next system with Status: Not Started → offer $ccgs-design-system option
- Is the verdict PASS or CONCERNS on a review that ran both passes? → offer $ccgs-gate-check or $ccgs-create-architecture. A focus run (`consistency` or `design-theory`) checked one pass, so it never offers either

Build the option list dynamically — only include options that apply:

**Option pool:**
- `[_] Plan a separate fix: [W-XX description] in [gdd-name].md — [effort estimate]` (one option per simple-edit warning; only for Warning-level, not Blocking)
- `[_] Run $ccgs-design-review [flagged-gdd-path] — address flagged warnings` (one per flagged GDD, if any)
- `[_] Run $ccgs-design-system [next-system] — next in design order` (always include, name the actual system)
- `[_] Run $ccgs-create-architecture — begin architecture (verdict is PASS/CONCERNS)` (include only if the verdict is PASS, or CONCERNS explicitly accepted by the user, on a review that ran both passes — never on FAIL, NOT ASSESSED or a focus run)
- `[_] Run $ccgs-gate-check — validate Systems Design phase gate` (include if verdict is PASS on a review that ran both passes)
- `[_] Stop here`

Assign letters A, B, C… only to included options. Mark the most pipeline-advancing option as `(recommended)`.

Return the verdict and next step without running it or writing a decision log.
A subsequent coordinator action can retain findings and apply authorized fixes.

---
