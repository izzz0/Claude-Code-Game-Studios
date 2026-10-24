# Framework validation

Run `python -m unittest discover -s studio-tests/codex -v` from the repository
root. These tests validate Codex skill structure and the migrated helper behavior,
using temporary projects, fixtures and stub executables. They do not validate a
game or replace real engine execution.

For behavioral validation, copy the template to an isolated temporary directory
and give an independent agent a small game request. Exercise $ccgs-start through
$ccgs-story-done and inspect the artifacts, not just the agent's final answer.
Repeat story creation with the same brief, resume an interrupted story, and
withhold a required engine or screenshot to verify that it remains incomplete.
Run a minimal game with a real available engine and actually open its screenshot.
Report any engine/platform that was not exercised.
