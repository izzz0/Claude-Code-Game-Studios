# $ccgs-prototype — Phase 4: Plan the Prototype

> Part of `$ccgs-prototype`. `SKILL.md` names when to read this file; the settings it
> resolved and the rules under its later headings still apply here.

## Phase 4: Plan the Prototype

Define in 3–5 bullet points the minimum viable prototype:

- What is the falsifiable hypothesis?
- What is the riskiest assumption — and how does this prototype test it first?
- What is the absolute minimum needed to answer the question?
- What is explicitly cut? (menus, save systems, error handling, polish, architecture — all of it)

**Scope constraint:** A concept prototype tests ONE mechanic — not the whole game.
If scope covers more than one mechanic, cut it down. When in doubt, cut more.

Present the plan and resolve material scope choices before building. Planning
itself is read-only. Once execution is authorized, the coordinator records the
development checkpoint, if `features.session_state` is enabled, in
`production/session-state/active.md`
(create `production/session-state/` if it does not exist). Include: concept name,
hypothesis, path chosen, scope bullet points, and current phase ("Phase 5 —
Implement"). This lets the next session resume without starting over if the session
ends mid-build — especially important for multi-day Engine path work.

---
