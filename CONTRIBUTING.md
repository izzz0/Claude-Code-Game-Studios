# Contributing

Keep the nine minimal-workflow skills small, actionable and consistent with
AGENTS.md and .agents/studio/docs/core-workflow.md. Add capability only when it
supports the core route; do not restore unused studio roles or automatic hooks.

Use a branch and a pull request. Describe the concrete behavior and validation.
Keep helper output observational: the calling skill interprets facts and does
not equate helper success with game success.

Run `python -m unittest discover -s studio-tests/codex -v` before submitting.
For a substantial skill change, exercise a realistic request in an isolated
temporary game project, and report what was actually run. Keep generated
artifacts and personal configuration out of the framework checkout.

Preserve the upstream MIT license and attribution for reused code.
