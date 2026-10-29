> Gate definition, loaded by `$ccgs-gate-check` for the TARGET PHASE ONLY.
> Never load the other five — one gate applies per invocation.


# Gate: Systems Design → Technical Setup


**Required Artifacts:**
- [ ] Systems index exists at `design/gdd/systems-index.md` with at least MVP systems enumerated
- [ ] All MVP-tier GDDs exist in `design/gdd/` and individually pass `$ccgs-design-review`
- [ ] A cross-GDD review report exists in `design/gdd/` (from `$ccgs-review-all-gdds`)

**Quality Checks:**
- [ ] All MVP GDDs pass individual design review (8 required sections, no MAJOR REVISION NEEDED verdict)
- [ ] `$ccgs-review-all-gdds` verdict is not FAIL (cross-GDD consistency and design theory checks pass). A NOT ASSESSED verdict does not satisfy this: that review could not compare the GDDs, so this item is NOT ASSESSED for the gate. Nor does a focus-run report (its `Focus:` line names one pass only): the other pass never ran, so the item stays open until a review runs both
- [ ] All cross-GDD consistency issues flagged by `$ccgs-review-all-gdds` are resolved or explicitly accepted
- [ ] System dependencies are mapped in the systems index and are bidirectionally consistent
- [ ] MVP priority tier is defined
- [ ] No stale GDD references flagged (older GDDs updated to reflect decisions made in later GDDs)

## Workflow tier reductions

The checklist above is the **`full` baseline**. At lower tiers apply the
reduction for the resolved tier; items not named keep their status above.
Reductions only ever *relax* a requirement — `workflow_overrides` is the
only thing that adds one.

- **`full`** — systems-index + all MVP GDDs at 8 sections + cross-GDD review report all required
- **`standard`** — MVP GDDs validated at the **5 standard sections** (+ conditional Formulas); cross-GDD review report → recommended
- **`minimal`** — **gate not applicable** — no gate between brief and code; emit an explicit `NOT APPLICABLE` result (not a quality PASS)

> **`minimal` "not applicable" gate.** The Systems Design → Technical Setup gate
> has no meaning at `minimal` (no GDDs exist by design). Return an explicit
> `NOT APPLICABLE — no design gate at minimal workflow` result, with no quality
> PASS and no stage write from this invocation. Route directly to the minimal
> brief → code path; do not flag absent GDDs as blockers. The director panel does
> not run for it.
