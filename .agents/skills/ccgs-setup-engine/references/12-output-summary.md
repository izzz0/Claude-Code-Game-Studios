# $ccgs-setup-engine — Section 12: Output Summary

> Part of `$ccgs-setup-engine`. `SKILL.md` names when to read this file; the settings it
> resolved and the rules under its later headings still apply here.

## 12. Output Summary

After setup is complete, output:

```
Engine Setup Complete
=====================
Engine:          [name] [version]
Language:        [GDScript | C# | GDScript + C# | C# | C++ + Blueprint | Blueprint + C++]
Knowledge Risk:  [LOW/MEDIUM/HIGH]
Reference Docs:  [created/skipped]
AGENTS.md:       [updated]
Tech Prefs:      [created/updated]
project.yaml:    [created/updated]
Engine role guidance:     [verified / NOT ASSESSED, from actual inspection]

Next Steps:
1. Review docs/engine-reference/<engine>/VERSION.md
```

Then print **one** Next-Steps list, matching the resolved `workflow` tier:

**`minimal` — the lean 4-step floor (you are on step 1):**
```
2. Run $ccgs-brainstorm to produce your one-page design/game-brief.md (the lean-tier design artifact)
3. Run $ccgs-create-stories to turn the brief's MVP list into stories
4. Run $ccgs-dev-story — first line of game code
```
(No `$ccgs-map-systems`, `$ccgs-design-system`, `$ccgs-prototype`, or `$ccgs-sprint-plan` at
`minimal` — the brief replaces the GDDs and its build order is the plan.)

**`standard` / `full` — the full pipeline:**
```
2. [If from $ccgs-brainstorm] Run $ccgs-map-systems to decompose your concept into individual systems
3. [If from $ccgs-brainstorm] Run $ccgs-design-system to author per-system GDDs (guided, section-by-section)
4. [If from $ccgs-brainstorm] Run $ccgs-prototype [core-mechanic] to validate the core idea before writing GDDs
5. [If fresh start] Run $ccgs-brainstorm to discover your game concept
6. Create your first milestone: $ccgs-sprint-plan new
```

---

Verdict: **COMPLETE** — engine configured and reference docs populated.