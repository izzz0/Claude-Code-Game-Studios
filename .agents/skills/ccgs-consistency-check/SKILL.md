---
name: ccgs-consistency-check
description: "Scan GDDs against the entity registry for cross-document conflicts. Grep-first approach targets conflicting sections, different stats."
---

Run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow` and use its output.



# Consistency Check

Detects cross-document inconsistencies by comparing all GDDs against the
entity registry (`design/registry/entities.yaml`). Uses a grep-first approach:
reads the registry once, then targets only the GDD sections that mention
registered names — no full document reads unless a conflict needs investigation.

**This skill is the write-time safety net.** It catches what `$ccgs-design-system`'s
per-section checks may have missed and what `$ccgs-review-all-gdds`'s holistic review
catches too late.

**When to run:**
- After writing each new GDD (before moving to the next system)
- Before `$ccgs-review-all-gdds` (so that skill starts with a clean baseline)
- Before `$ccgs-create-architecture` (inconsistencies poison downstream ADRs)
- On demand: `$ccgs-consistency-check entity:[name]` to check one entity specifically

**Output:** Read-only conflict report and proposed registry corrections

---

Every
`native user-input mechanism` call follows `.agents/studio/docs/automation-modes.md`
(collaborative reviews major drafts · guided raises material decisions · autonomous records decisions;
`automation_always_ask` categories always prompt).

**`workflow`** (see `.agents/studio/docs/workflow-modes.md`), applied per GDD at its
**effective** tier — the `system_overrides` row for that GDD's system (its
filename stem) when the block lists one, else the project value:
- `full` — full entity-registry cross-check against all GDD sections.
- `standard` — cross-check against the required sections only. The report's
  Scope line says so, and each value stated for a registered name outside those
  sections is listed as not checked at this tier (Phase 3 applies this).
- `minimal` — not meaningful (no GDDs to check).

## Phase 1: Parse Arguments and Load Registry

**Modes:**
- No argument / `full` — check all registered entries against all GDDs
- `since-last-review` — check only GDDs modified since the last review report
- `entity:<name>` — check one specific entity across all GDDs
- `item:<name>` — check one specific item across all GDDs

**Load the registry:**

```
Read path="design/registry/entities.yaml"
```

If the file does not exist or has no entries:
> "Entity registry is empty. Run `$ccgs-design-system` to write GDDs — the registry
> is populated automatically after each GDD is completed. Nothing to check yet."

Verdict: **NOT ASSESSED — entity registry empty**. Stop: nothing was compared,
so there is no PASS to give and nothing to write.

Build four lookup tables from the registry:
- **entity_map**: `{ name → { source, attributes, referenced_by } }`
- **item_map**: `{ name → { source, value_gold, weight, ... } }`
- **formula_map**: `{ name → { source, variables, output_range } }`
- **constant_map**: `{ name → { source, value, unit } }`

Count total registered entries. Report:
```
Registry loaded: [N] entities, [N] items, [N] formulas, [N] constants
Scope: [full | since-last-review | entity:name]
```

For `entity:<name>` or `item:<name>`, if the registry has no entry by that name
the verdict is **NOT ASSESSED — `<name>` is not in the registry**: list the
closest registered names and stop. Checking an unregistered name compares
nothing, and that is not a PASS.

---

## Phase 2: Locate In-Scope GDDs

```
Glob pattern="design/gdd/*.md"
```

Exclude the docs that live in `design/gdd/` but are not system GDDs:
`game-concept.md`, `systems-index.md`, `game-pillars.md`, `gameplay-tags.md`,
`entity-registry.md`, `fixture-swap-ledger.md`, `sound-bible.md` and any
`gdd-cross-review-*.md` (the report `$ccgs-review-all-gdds` writes here).

For `since-last-review` mode:
```bash
git log --name-only --pretty=format: -- design/gdd/ | grep "\.md$" | sort -u
```
Limit to GDDs modified since the most recent `design/gdd/gdd-cross-review-*.md`
file's creation date.

Report the in-scope GDD list before scanning. **If the list is empty** — no system
GDDs exist, or `since-last-review` found none changed — the verdict is
**NOT ASSESSED — no GDDs in scope**: say which filter produced zero, and stop.
A scan of nothing finds no conflicts, and that is not a PASS.

---

## Phase 3: Grep-First Conflict Scan

For each registered entry, grep every in-scope GDD for the entry's name.
Do NOT do full reads — extract only the matching lines and their immediate
context (-C 3 lines).

This is the core optimization: instead of reading 10 GDDs × 400 lines each
(4,000 lines), you grep 50 entity names × 10 GDDs (50 targeted searches,
each returning ~10 lines on a hit).

**In a GDD whose effective tier is `standard`, compare only hits under a
required section.** The effective tier is per GDD: `system_overrides.<stem>`
replaces the project tier for that GDD in either direction (a `full` row makes
every section compared). Grep each such GDD once for `^## ` to get its headings
and line numbers, and file every name hit under the nearest heading above it:
only hits under Overview, Detailed Rules / Detailed Design, Formulas, Edge
Cases, Dependencies or Acceptance Criteria are compared — plus Tuning Knobs when
`project.yaml` sets `workflow_overrides.tuning_knobs: true` (read that flag
once; it only ever adds the section). Any other hit (Tuning Knobs without the
flag, Player Fantasy, any other section) raises no finding and is not logged;
list each one that states a value (name, GDD, section) on the report's
`Not checked at this tier` line.

### 3a: Entity Scan

For each entity in entity_map:

```
Grep pattern="[entity_name]" glob="design/gdd/*.md" output_mode="content" -C 3
```

For each GDD hit, extract the values mentioned near the entity name:
- any numeric attributes (counts, costs, durations, ranges, rates)
- any categorical attributes (types, tiers, categories)
- any derived values (totals, outputs, results)
- any other attributes registered in entity_map

Compare extracted values against the registry entry.

**Conflict detection:**
- Registry says `[entity_name].[attribute] = [value_A]`. GDD says `[entity_name] has [value_B]`. → **CONFLICT**
- Registry says `[item_name].[attribute] = [value_A]`. GDD says `[item_name] is [value_B]`. → **CONFLICT**
- GDD mentions `[entity_name]` but doesn't specify the attribute. → **NOTE** (no conflict, just unverifiable)

### 3b: Item Scan

For each item in item_map, grep all GDDs for the item name. Extract:
- sell price / value / gold value
- weight
- stack rules (stackable / non-stackable)
- category

Compare against registry entry values.

### 3c: Formula Scan

For each formula in formula_map, grep all GDDs for the formula name. Extract:
- variable names mentioned near the formula
- output range or cap values mentioned

Compare against registry entry:
- Different variable names → **CONFLICT**
- Output range stated differently → **CONFLICT**

### 3d: Constant Scan

For each constant in constant_map, grep all GDDs for the constant name. Extract:
- Any numeric value mentioned near the constant name

Compare against registry value:
- Different number → **CONFLICT**

---

## Phase 4: Deep Investigation (Conflicts Only)

For each conflict found in Phase 3, do a targeted full-section read of the
conflicting GDD to get precise context:

```
Read path="design/gdd/[conflicting_gdd].md"
```
(Or use Grep with wider context if the file is large)

Read it by section: find the conflicting section's heading with the Grep tool
(pattern `^#`, content mode) and Read that range with offset and limit.

Confirm the conflict with full context. Determine:
1. **Which GDD is correct?** Check the `source:` field in the registry — the
   source GDD is the authoritative owner. Any other GDD that contradicts it
   is the one that needs updating.
2. **Is the registry itself out of date?** If the source GDD was updated after
   the registry entry was written (check git log), the registry may be stale.
3. **Is this a genuine design change?** If the conflict represents an intentional
   design decision, the resolution is: update the source GDD, update the registry,
   then fix all other GDDs.

For each conflict, classify:
- **🔴 CONFLICT** — same named entity/item/formula/constant with different values
  in different GDDs. Must resolve before architecture begins.
- **⚠️ STALE REGISTRY** — source GDD value changed but registry not updated.
  Registry needs updating; other GDDs may be correct already.
- **ℹ️ UNVERIFIABLE** — entity mentioned but no comparable attribute stated.
  Not a conflict; just noting the reference.

---

## Phase 5: Output Report

```
## Consistency Check Report
Date: [date]
Registry entries checked: [N entities, N items, N formulas, N constants]
GDDs scanned: [N] ([list names])
Scope: [all GDD sections | required sections only — workflow: standard | per GDD — name each GDD whose effective tier differs, and its tier]
Not checked at this tier: [each value stated outside the required sections (name, GDD, section) — or "none"; omit when every GDD is at `full`]

---

### Conflicts Found (must resolve before architecture)

🔴 [Entity/Item/Formula/Constant Name]
   Registry (source: [gdd]): [attribute] = [value]
   Conflict in [other_gdd].md: [attribute] = [different_value]
   → Resolution needed: [which doc to change and to what]

---

### Stale Registry Entries (registry behind the GDD)

⚠️ [Entry Name]
   Registry says: [value] (written [date])
   Source GDD now says: [new value]
   → Update registry entry to match source GDD, then check referenced_by docs.

---

### Unverifiable References (no conflict, informational)

ℹ️ [gdd].md mentions [entity_name] but states no comparable attributes.
   No conflict detected. No action required.

---

### Clean Entries (no issues found)

✅ [N] registry entries verified across all GDDs with no conflicts.

---

Verdict: PASS | CONFLICTS FOUND | NOT ASSESSED
```

**Verdict:**
- **CONFLICTS FOUND** — one or more conflicts detected. List resolution steps.
- **NOT ASSESSED** — nothing was compared: the entity registry is empty or the
  named entity is not in it (Phase 1), or no GDDs were in scope (Phase 2). Say
  which.
- **PASS** — no conflicts. Registry and GDDs agree on all checked values, across at least one GDD.

---

## Phase 6: Proposed Registry Corrections

Keep this check read-only. Return proposed changes rather than editing the
entity registry, GDDs, consistency log or execution checkpoint.

For each stale entry, name its current value, source GDD/section, proposed value,
revision date and the old value to retain in history. For an unregistered fact,
propose an entry only if more than one GDD uses it. Propose deprecation rather
than deleting an entry that disappeared from all GDDs.

Include the current registry hash. After the review, an authorized coordinator
must re-read it before applying a proposal and validate changed entries with
`bash .agents/studio/scripts/registry.sh validate`. A conflict or concurrent
change requires reconciliation rather than overwriting the newer registry.

For each conflict, return a proposed `docs/consistency-failures.md` entry with
date, involved documents, differing values, resolution or unresolved blocker,
and the general lesson. Do not create or append the log during this check.

## Phase 7: Read-only Handoff

Return the actual scope, compared GDD count, conflict count, verdict, protected
input hashes and next action. Include a checkpoint summary in the response for
the coordinator to retain after the check; do not update `active.md` here.
PASS requires at least one actual comparison. Conflicts block downstream
architecture work; missing inputs remain NOT ASSESSED.
