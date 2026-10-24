# Core workflow

Read this once when a studio skill starts, then load only the relevant template
or pinned engine reference. Skills are instructions executed by Codex, not a
background daemon or an automatic team of 49 agents.

## Root and prerequisites

Locate the repository containing this skill and its project.yaml, and run all
commands with that directory as the working directory. Do not use an unrelated
parent project. Scripts that support --root can target an explicit project.
The configuration helper locates the template from its own file when launched
from a subdirectory; a nested project's own config takes precedence.

Requirements: Git, Bash (Git for Windows on Windows), awk/sed/coreutils and a
working Python 3 on PATH. Check `bash --version` and `python --version`; the
Windows Store alias alone is not a working Python. Dependencies and the chosen
game engine are separate. Do not silently install an engine or paid package.

## Resolve, then act

Run explicitly, from the project root:

    bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,qa.level,review_mode,testing.strict,engine_values
    bash .agents/studio/scripts/project-state.sh

Resolve a system-specific tier with `resolve_config <system-slug> --keys workflow,qa.level`.
Read .agents/studio/docs/effects-map.md for configuration semantics. Inspect
reported notes and diagnostics: helper success alone does not establish valid
configuration. A local file without its base or invalid/unreadable configuration
must be corrected before state-changing work; do not continue with guessed defaults.

Configuration order is whitelisted local overrides, project config, legacy
mirrors, rigor expansion for its six knobs, then terminal defaults. Existing
explicit values win. The six knobs are modes.workflow, docs.density, qa.level,
modes.story_granularity, modes.review_mode and team.size. Never seed them merely
to set up a new minimal project: that would shadow subsequent rigor changes.
The v1 entrypoints support only rigor/workflow minimal. If rigor or the effective
workflow for the current system is standard/full, report the unsupported tier
and pause that workflow; never downgrade it. Do not treat qa.level as workflow.

Initialize only absent modes.rigor=minimal and modes.automation=guided.
For a scalar config edit, preview with:

    bash .agents/studio/scripts/config-set.sh modes.rigor minimal --dry-run

Then repeat without --dry-run when the edit belongs to the authorized task.
Read back the output. Write stage through set-stage.sh so the YAML and legacy
stage mirror agree. Preserve unrelated keys and user-defined commands. An
explicit request is authorization for ordinary edits; modes do not override it.

## Collaboration

Guided (default): explain the intended outcome briefly, execute routine edits
and checks, and ask only about significant product/architecture choices,
out-of-scope changes or missing necessary information.
Collaborative: present each major phase's draft for review before implementing.
Autonomous: decide within the accepted scope and record meaningful choices.
Respect configured automation_always_ask categories and existing authorization;
none of these settings expands the task or the environment's permissions.
If a required answer is pending, preserve progress and wait.

No model is pinned. One agent may perform the workflow. Where a second agent
adds useful independence, delegate a bounded question and report that review
accurately; never invent an agent invocation.

## Engine configuration

Pin engine.name (Godot, Unity or Unreal), engine.version and engine.language.
Record engine.path when known, platform targets and useful commands in
project.yaml. The path is an editor executable for Godot/Unity and the engine
installation root for Unreal. Code roots: src/, Assets/, Source/ respectively.
Do not use a detected src/ folder to infer that an unconfigured game is Godot.
Preserve an existing engine and project; changing either is a significant choice.

Read docs/engine-reference/<engine>/VERSION.md and only the relevant module
references. These shipped snapshots are starting points, not proof that their
version matches the user's installation. Check the executable/version and
official engine documentation; update the pin and references for the chosen
version without claiming unverified APIs work.
Godot can scaffold project.godot and a small launchable scene. Unity/Unreal
projects must be created with their installed editor/tooling; do not fabricate
a valid project or a successful import when that tooling is unavailable.

Commands may be scalar or OS-specific maps (windows/linux/macos). Resolve the
current OS key rather than executing the map as text. commands.test runs game
tests, commands.smoke performs a compile/import check, commands.run launches the
actual game. Ask for a missing command when it cannot be derived from the
existing engine project. A setup can record a chosen engine even when it is
unavailable; implementation/verification remains blocked where it needs it.

## Brief, stories and recovery

Minimal uses design/game-brief.md, not a mandatory GDD or architecture document.
Its MVP list is the scope and Build order is the sequence. One feature becomes
one story under production/epics/<epic-slug>/story-NNN-<feature-slug>.md.
Use templates/game-brief.md and templates/story.md from this directory.
On a return visit, inspect all existing epic/story files before allocating the
next number. Never overwrite or renumber a story. Match existing feature scope
before adding stories; rerunning an unchanged brief creates nothing.

Story states: Ready -> In Progress -> In Review -> Complete. Unresolved
dependencies remain Blocked. Interrupted work remains In Progress with its
next action recorded, not Complete. Read story-facts.sh and story-status.sh for
observations. Keep each story's header and any matching sprint-status.yaml
entry consistent; preserve unrelated sprint entries.
If a story names an ADR, verify the file exists and its Status is Accepted.
Minimal does not create or require ADRs for work that names none.

Update the session checkpoint through session-state.sh checkpoint (stdin).
Include branch, story path, actual files, next step, blockers and run result.
Its template is templates/session-state.md. Read it manually after restart;
there is no session-start hook. Honor features.session_state=off.
Narrative appends must not replace the bounded checkpoint markers.

## Run tests and interpret results

For gdUnit4, Unity Test Framework or Unreal Automation use the existing test runner:

    bash .agents/studio/scripts/test-run.sh <engine> --dry-run
    bash .agents/studio/scripts/test-run.sh <engine> --log production/qa/test.log

The engine argument is godot, unity or unreal. It reads commands.test and
engine.path; --cmd/--exe can override that framework's command/path.
Never substitute an ad-hoc echo or a stub for real game validation.
Inspect ran, precheck, import_exit/build_exit, exit, timed_out, zero_tests,
results_file, tests, rule and log. Exit 0 from the HELPER only means facts were
emitted. A test file existing or a stub editor succeeding proves no game behavior.

For GUT or another custom runner, preserve commands.test and run the resolved
command directly from the project root under a timeout, retaining stdout/stderr
and its actual exit code in production/qa/. Create that directory first.
Use the runner's documented result format and test counts; do not apply gdUnit4
or Unity exit-code meanings to it. Record a zero-test result or unrecognized
output as NOT ASSESSED. A command exiting 0 alone is not a test PASS.
The built-in helper's framework precheck is not evidence that custom tests failed.

- PASS requires actual execution, a recognized success result and evidence that
  tests ran; inspect logs when counts are unknown.
- FAIL means actual failures/crashes, or a timeout during a required test run.
- NOT ASSESSED means no usable runner, zero tests, missing results, an unsupported
  result or absent evidence. Report why and preserve the incomplete story.
- At qa.level minimal, unconfigured automated tests may be explicitly WAIVED
  when the story has no stricter test requirement. This is never a test PASS.
  Existing failing tests remain failures. Higher configured QA or strict checks
  are not waived; explain any unsupported evidence requirement.

Parse/import checks and game tests are separate. Godot's parser helper lives at
res://.agents/studio/scripts/godot-parse-check.gd; import first. For Unity use the
configured smoke command; Unreal requires a successful editor-target build.

## Run and observe

For every player-visible change, use commands.run to launch the actual game
windowed at a fixed resolution (1280x720 unless the project says otherwise).
Reach the acceptance criterion's state, not just the title screen.
Check engine.path and normal installation locations before concluding an
engine is unavailable merely because it is missing from PATH.

Retain images under production/qa/evidence/<story-slug>/ and open them with the
host's image viewer. Record what was actually observed and image paths in
<story-slug>-evidence.md beside the images. Headless tests, text descriptions,
an unopened image and a user's generic “yes” are not visual evidence.
Still images establish layout/presence, not input feel, timing or audio; record
those as separate playtest checks when the acceptance criteria require them.

Capture mechanisms (verify against the pinned engine version):

- Godot: windowed scene launch with --write-movie <absolute-path>.png and
  --quit-after 60 produces a numbered frame sequence. Open a rendered frame.
  A viewport screenshot after frame_post_draw can capture a deeper state.
- Unity: launch a built player or editor play mode, with rendering enabled;
  use ScreenCapture.CaptureScreenshot after reaching the required state.
  Custom --scene/--screenshot switches require an implemented bootstrap.
- Unreal: standalone -game launch with a positional map URL and a delayed
  HighResShot command. On Git Bash use MSYS_NO_PATHCONV=1 for /Game map URLs and
  an absolute .uproject path; bound the launch duration. Do not quit in the same
  frame as the capture.

Use the environment's approved computer-use capability or OS capture if native
capture is unsuitable. Avoid headless, nographics or null-rendering flags for
visual observation. Keep background helper windows hidden on Windows unless
the user needs to see/control the game itself.

Emit exactly one line in each implementation result and preserve it in evidence:

    Run result: OBSERVED — <observed state and retained image path>
    Run result: NOT VERIFIED — <reason>
    Run result: N/A — <why the change has no player-observable surface>

Choose one shape. NOT VERIFIED blocks completion of visible work at every QA
level. An unavailable engine/capture tool is a limitation to report, not a pass.

## Review and completion

Code review reads the actual files and requirements. Report actionable defects
with locations, behavior and evidence. Distinguish self-review from independent
review. It does not silently fix files or force architecture unrelated to scope.

For evidence freshness:

    bash .agents/studio/scripts/review-receipts.sh hash <changed-files>
    bash .agents/studio/scripts/review-receipts.sh check <stamp-file>

Capture hash output into the evidence stamp. Check all required paths exist;
the helper intentionally omits an unstamped absent literal path. Report changed
or missing inputs, and judge whether their acceptance criteria need new checks;
a hash is a freshness observation, not a pass/fail verdict.

Completion maps every AC to a current observed/tested result or an explicitly
applicable minimal test waiver. Missing evidence is NOT ASSESSED, not passed.
Resolve material review findings. Mark Complete, update any matching sprint
entry and checkpoint only when all required criteria are established. Report
remaining uncertainty without checking unsupported AC boxes.
