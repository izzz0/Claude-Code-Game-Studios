# Focused Cocos and nine-team acceptance

Status: **NOT ASSESSED — nine native teams remain open; original game optimization has not started.**

The bounded Cocos Web integration gate has an independent **PASS**. This is
separate from the still-open nine-team gate below.

The user paused Godot real runs and the exhaustive 74-skill campaign. The active
gate is nine actual Cocos team workflows, then Cocos Web integration, then
authorized full + guided optimization of the original game. Other skills may be
used with validation as needed. This change does not establish full-port acceptance.

## Fresh Cocos Web baseline

Local evidence root: `.scratch/cocos-acceptance-20261028/`.
The source manifest covers 861 authored files, SHA256
`a28ea860155137381d3fea97f66e59ea0c4c5d1e05ee8b986904a6b7df204929`.
All 861 original files and 861 copied files still matched that manifest after the
browser runs. No original-game source, assets, meta files or configuration changed.

| Scenario | Expected | Observed | Evidence | Status |
|---|---|---|---|---|
| Fresh dependencies and type checks | Install and both TS checks succeed | npm ci, server/core check and client check exit 0 | `evidence/baseline-report-portable.json`, `01-ci.log`, `02-run-typecheck.log`, `03-typecheck-client.log` | PASS |
| Real Node game tests | Nonzero actual tests, no failure/skip/cancellation | 26 tests, 26 pass, all other counts zero | `evidence/04-test.log` | PASS |
| Studio Cocos test adapter | Read actual TAP counts, not helper exit alone | Configured isolated full + guided project; dry-run and real `test-run.sh cocos` resolved the Node command and parsed26/26, recognized TAP, no timeout, result PASS | `evidence/adapter-live.json`, `adapter-live.tsv`, `game/production/qa/adapter-live.tap` | PASS |
| Server and Creator Web build | Actual success code, fresh outputs | Server exit 0; Creator 3.8.8 exit 36 correctly mapped to wrapper 0; fresh Web assets | `evidence/05-build-server.log`, `06-build-client-web-mobile.log`, portable report per-file hashes | PASS |
| Actual local Web start | Served package and backend respond | Browser loaded rendered game on loopback18089; backend18787 health returned success | `evidence/gui/01-lobby.png`, `gui-observations.json` | PASS |
| Two-player room and readiness | Both roles in same room, actual countdown | Room637703 joined by two pages; ready/countdown and live synchronized race observed | `evidence/gui/04-two-player-room.png`, `gui-observations.json` | PASS |
| Character preview/synchronization | Selected character appears in peer room | Thief chose 威龙; police page reflected it | `evidence/gui/05-character-preview.png`, `06-character-sync-peer.png` | PASS |
| Committed Chinese text | Input affects actual score/state | Actual field input yielded 11-streak/100%; later police36-streak and capture | `evidence/gui-observations.json`; screenshots07,10,11 | PASS |
| Actual Chinese IME | No pre-selection miscount or duplicate commit | User manually used their normal IME and reported no error | User response retained in `evidence/gui-observations.json` | PASS, human-reported |
| Capture and timeout outcomes | Both peers agree with rules | Police won capture; thief won timeout, with corresponding peer defeats | `evidence/gui/08-thief-timeout-win.png` through `11-thief-capture-outcome.png` | PASS |
| Another match after settlement | Reset and run new race | Returned from settlement, created956756, both joined/readied and played second race | `evidence/gui-observations.json` | PASS |
| Real connection loss/recovery | Same running race resumes, input still works | Proxy connection2 dropped;3 opened503ms later; backend reconnects1, no forfeit; resumed input and eventual timeout settlement | `evidence/reconnect-events.jsonl`, screenshots12–16, GUI audit | PASS |
| Multiple code roots and generated mirror guard | Four authored roots writable, generated mirrors protected | New integration regression caught nested shared mirror bypass; guard fixed, positive and negative paths pass | `studio-tests/codex/test_hooks.py` | PASS, protocol regression |

Browser screenshots were saved and viewed. Their hashes and file timestamps are
in `evidence/gui-observations.json`. IME is a human observation, not a recording
of candidate-window/composition events. The brief disconnected intermediate
frame was not captured; proxy timestamps, backend counters, resumed game state
and subsequent input provide the reconnect proof. Viewport overrides and test
server settings were restored. Browser error collection for the second page was empty.

Original baseline logs using colon filenames were NTFS alternate streams.
They were exported byte-for-byte to ordinary portable filenames; export hashes
are in `baseline-report-portable.json`. That report is a derived archive index,
not a new execution, and the originals remain retained.

Independent reviewer `/root/review_cocos_baseline` opened eight key images and
verified all861 source/copy hashes, all16 screenshot hashes and all198 build
artifact hashes. The complete returned review is retained verbatim at
`evidence/independent-cocos-review.md` with identity/hash metadata in the adjacent
JSON file. Its PASS is limited to Cocos Web integration; it does not establish
native team-role execution. IME remains explicitly human-reported.

## Nine native Cocos teams

Only these entries are selected; do not run `--all` for this focused campaign.
The other65 authored cases and their historical records remain unchanged.
All nine scenarios use Cocos3.8.8/TypeScript, current role contracts, actual child
identities, same-task interruption/resume and a distinct read-only reviewer.
The existing registered engine-programmer is explicitly configured as Cocos
primary in each fixture; no Godot role is selected.

| Team | Isolated scenario | Actual native status |
|---|---|---|
| combat | Existing chase/capture/timeout rules | First attempt NOT ASSESSED: missing Cocos primary; second FAIL: run-label/identity confusion; third dispatched8 actual roles and completed7 tasks, then NOT ASSESSED: model capacity interrupted independent review |
| UI | Chase HUD, connection warning,200% scale, restart | NOT ASSESSED — not reached |
| QA | Failed Web entry smoke, read-only negative gate | First run completed3 actual children/recovery but retained NOT ASSESSED for an opaque hashing pipeline; next run interrupted by the Windows patch launcher's unsandboxed-retry approval request |
| audio | Countdown/capture/timeout cue draft | NOT ASSESSED — not reached |
| level | City track and boundaries | NOT ASSESSED — not reached |
| live-ops | Local event/config drafts only | NOT ASSESSED — not reached |
| narrative | Help and settlement copy, consistency review | NOT ASSESSED — not reached |
| polish | Feedback risks, actual-measurement requirements | NOT ASSESSED — not reached |
| release | Missing local package/sign-off blocks release | NOT ASSESSED — not reached |

Retained native evidence:
`.scratch/full-acceptance-20261025/native-project/.scratch/cocos-team-acceptance/`.
Combat attempts `4740a3e8cc14` and `9331286bf846` are original records, not overwritten
or reassessed as PASS. The second did return a real child identity, but no completed
required team/recovery/review evidence. `team-run.py init --id` is a local record
slug; `event --agent-id` preserves the actual host path or UUID. A new regression
executes that distinction without claiming real agent execution.

Third attempt `ae97fc14b79c` retained native game-designer, gameplay-programmer,
AI scope reviewer, technical-artist, engine-programmer, sound-designer, QA tester
and independent QA-lead identities. Its manifest records seven completed tasks;
the final reviewer did not complete. The native host returned `serverOverloaded`.
Neither partial artifacts nor a model-capacity failure establish team PASS.

That run also exposed an evaluator defect: implementation children were being
considered reviewer candidates before review-manifest matching. The fix filters
only the claimed actual reviewer identities and keeps write/role/parent checks.
A separate review found that new deliverables were absent from the initial input
bundle. The evaluator now binds the same reviewer to final expected output
contents/hashes as well as supplied inputs, failing closed on missing/unreadable
outputs. Counterexamples cover fixture-only review, unrelated writers, final
output reads, legacy prompt binding and changes after review. Historical native
records are unchanged; these evaluator fixes still need a new native execution.

QA attempt `71c8d80d0366` subsequently exercised real QA-lead, QA-tester and
independent engine-programmer children. Their full histories and original
records are retained. The supplied failed smoke correctly stopped later QA
phases. However, the reviewer also ran an unqualified `Get-FileHash | Format-List`
pipeline whose host receipt was opaque; strict read-only proof therefore remains
NOT ASSESSED. Updated Windows instructions keep hashing/configuration helpers
with the coordinator and prescribe auditable literal reads for all read-only
children. The verifier whitelist is unchanged. A redundant requirement that the
answer literally say `read-only` was removed; actual protected-file hashes and
all three native evidence predicates remain mandatory. A protocol regression
proves the resulting answer cannot pass without evidence or after a protected
write. Neither this fix nor the child's self-reported PASS reclassifies the
original native NA. The next attempt `4b1e8cf63bf2` was interrupted by
`item/fileChange/requestApproval` (`command failed; retry without sandbox?`)
while the coordinator tried to retain the returned strategy inside the authorized
observations directory. The driver did not approve it. Updated guidance uses
bounded workspace file I/O/atomic retention instead, keeps the inherited sandbox,
and stops if that bounded write is also denied. No permission/approval handler was
weakened. Review retention additionally requires one complete verbatim artifact;
valid hashes cannot legitimize a coordinator-added approval prefix or duplicate
review artifacts. Its counterexamples passed with all49 evidence regressions.

Cases intentionally test orchestration and correct negative quality gates.
Even nine case PASS results would not prove actual audio, measured performance
or release-quality approval from fixtures without those inputs. Inspect each
active role, dependency, owned artifact and independent verdict before closing
the team gate; honest missing game-quality evidence remains NOT ASSESSED.

## Framework checks and recovery

- A source snapshot including the generated-mirror fix and first four Cocos
  scenario tests passed Windows244/244 and Linux244/244, zero skips.
- Source `35b34ba54e59e39e9101ee437a15e1cb7ebd20f4` passed hosted Windows245/245
  and Linux245/245, zero skips. Run `40706589644`, jobs `122880260925` and
  `122880263049`; logs are retained as `evidence/ci-35b34ba-windows.log` and
  `ci-35b34ba-linux.log`. Local Windows245 passed too; the local Linux suite
  printed245/245 OK but its surrounding shell wrapper had an exit-argument error,
  which is not presented as a successful wrapper run. Hosted Linux exited cleanly.
- Reviewer-candidate/final-output binding source
  `4c035202092f6535862b867a84242f8c829e89d1` passed250/250 on both local platforms
  and hosted CI, zero skips. Hosted run `40711427344`, Windows job `122897442519`
  and Linux job `122897442782`; receipt `evidence/ci-4c03520.json`. The earlier
  local shell-wrapper error was corrected and this later local Linux run exited0.
- Source `01cad7df8a17b222f91dfe385615a7a7906aa184` passed hosted Windows251/251
  and Linux251/251, zero skips. Run `40716161377`, jobs `122914311474` and
  `122914311989`; receipt `evidence/ci-01cad7d.json`.
- Subsequent bounded-retention guidance and the strict verbatim review regression
  passed24 driver and49 evidence tests. The resulting252-test source needs new CI.
- Independent review verified Cocos inputs, release negative gates, run labels,
  claimed reviewer selection and final-output binding. An earlier follow-up quota
  failure remains historical; subsequent read-only follow-ups completed without
  additional actionable findings. They do not replace native acceptance.
- Resume only the nine selectors with `--resume`, from the ordinary Git host,
  preserving inherited model/provider/permissions and existing Hook trust.
  No new Hook definition or global configuration is installed.

Unity, Unreal, paused Godot work, unused skills and untested mini-game devices
remain unverified. Original-game optimization is gated until required team and
Cocos integration acceptance is complete. No merge or release is authorized.
