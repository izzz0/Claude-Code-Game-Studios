# $ccgs-smoke-check — Phase 6: Write and Gate

> Part of `$ccgs-smoke-check`. `SKILL.md` names when to read this file; the settings it
> resolved and the rules under its later headings still apply here.

## Phase 6: Write and Gate

**In this file:**

- `qa.level` first
- Resolve the gate enforcement level
- Per verdict: FAIL, NOT ASSESSED, PASS WITH WARNINGS, PASS

Present the full report in conversation, then ask:
- Proceed within the accepted task scope and report the destination and evidence.

Write only within the accepted task scope.

**First apply `qa.level` (resolved earlier).** At `qa.level: minimal`, only a
genuinely unconfigured test suite may be explicitly `WAIVED` when no stricter
story requirement exists. A configured suite that runs and fails remains `FAIL`
and blocks hand-off. Otherwise, continue with the same FAIL rules:

**Resolve the gate enforcement level.** A FAIL verdict blocks QA hand-off; it
is not converted into an advisory hand-off by a strictness setting. The
`testing.strict` block **resolved in the resolved-config block at the top of this skill** (which merges
`project.local.yaml` over `project.yaml` — read that block, not the file, or a
developer's local override is silently ignored):

1. Read `testing.strict.config` only for reporting; it has no effect on whether
   a smoke FAIL blocks hand-off.
2. Do not read any strictness value as permission to continue after a smoke
   failure; surface it for context only.

After writing, deliver the gate verdict:

**If verdict is FAIL:**

"The smoke check failed. Do not hand off to QA until these failures are
resolved:

[List each failing automated test or smoke check with a one-line description]

Fix the failures and run `$ccgs-smoke-check` again to re-gate before QA hand-off."

**If verdict is NOT ASSESSED:**

"The smoke check could not establish build health — it did not fail, it did not
run. Do not hand off to QA on this result:

[Name each check that could not execute, and why: suite unconfirmed NOT RUN,
`PlayMode: NOT RUN`, zero tests executed, runner not installed, engine
executable not found, no build, build not launched this session, platform
unavailable]

[For each, the one thing that would make it runnable — e.g. 'confirm the suite
result from your IDE or CI', 'run `$ccgs-setup-engine`', 'set `engine.path`',
'produce a build', 'launch the build and play the checks'.]

Re-run `$ccgs-smoke-check` once any of those is resolved."

This outcome is **not governed by `testing.strict.config`**. That setting does
not turn a missing result into a pass, and reading an unrun check as advisory-therefore-fine is
the exact substitution this verdict exists to prevent. Say what could not be
checked and let the user decide — do not resolve it to either pass or FAIL on
their behalf.

**If verdict is PASS WITH WARNINGS:**

"Smoke check passed with warnings. The build is ready for manual QA.

Advisory items to resolve before running `$ccgs-story-done` on affected stories:
[list MISSING test evidence entries, and any runner warning — e.g. the orphan
count]

QA hand-off: share `production/qa/qa-plan-[sprint].md` with the ccgs-qa-tester
agent to begin manual verification."

**If verdict is PASS:**

"Smoke check passed cleanly. The build is ready for manual QA.

QA hand-off: share `production/qa/qa-plan-[sprint].md` with the ccgs-qa-tester
agent to begin manual verification."

---
