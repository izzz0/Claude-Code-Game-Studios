# Explicit pre-push quality checks

This is a retained proposal, not an installed Git pre-push hook. The native adapter observes supported tool calls but does not launch engines or models automatically before every push.

Before an authorized push, the coordinator runs the framework checks and applicable ccgs-smoke-check/regression checks, reads actual results and reports failures or unassessed requirements. Build, tests and visual runtime evidence remain separate.

Do not use example echo statements as build/test evidence. Missing engine, zero tests, timeout or absent result files cannot satisfy a required gate. Do not install .git/hooks, change host permissions or publish a release implicitly.
