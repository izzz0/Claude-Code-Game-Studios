# Native lifecycle hooks

The registration is .codex/hooks.json; the adapter is .agents/studio/runtime/hooks.py. The source baseline contains 18 hook/helper files; their responsibilities are mapped in studio-tests/migration-manifest.json. They are consolidated into native event handlers and preserved business helpers, not registered as eighteen independent background services.

Windows command registrations use the same direct `python` inline launcher for all ten events (without a leading `@`) so the definitions parse successfully in both `cmd.exe` and Windows PowerShell 5.1. The adapter remains responsible for emitting one JSON object on successful lifecycle events; shell execution does not grant trust or replace host review.

| Native event | Current responsibility |
| --- | --- |
| SessionStart | Bound project context, recovery location, missing-design guidance and event receipt |
| PreToolUse | Canonical Bash commit-snapshot checks; all native patch destinations; configured engine roots; checkpoint ownership; proposed-content write/registry observations |
| PostToolUse | Event receipt, actual asset JSON/naming observations, registry validation, changed-skill validation reminder |
| PreCompact / PostCompact | Recovery guidance and runtime receipt, without modifying developmental checkpoints |
| SubagentStart / SubagentStop | Native identity/event receipts; the coordinator validates the actual returned contract |
| Stop / Interrupt / SessionEnd | Bounded observational receipts; no automatic continuation or model invocation |

SessionEnd and Interrupt have a three-second maximum. Stop and SubagentStop always return JSON on successful exit. Runtime observation failures never request a Stop continuation. Duplicate receipts are deduplicated under OS locks; concurrent state updates use atomic writes and digest conflict checks.

Framework resources, active configuration and tool cwd are separate. Resource location is bound to this worktree. The nearest project.yaml/project.local.yaml within it selects configuration; native patch paths resolve from the event cwd. A separate nested Git worktree requires its own runtime rather than borrowing this project's hooks.

Runtime receipts live only in ignored .scratch/runtime. They contain safe native identity fields and a payload hash, not commands, credentials, QA attestations or checkpoint updates. A valid receipt proves the adapter ran for that payload; protocol fixtures can produce receipts too, so they do not establish trusted native-host execution by themselves.

Project configuration is still resolved by the original yaml-helper.sh; the adapter does not implement a second YAML parser. Business helpers emit observations, while commit-time malformed data blocks the pending commit. Existing registry IDs, localization freezes, protected artifacts and prototype boundaries remain checks. Explicit helper checks remain necessary on tool paths outside native hook coverage.

Review the exact definitions in the host before trusting them. Configuration, discovery, hook observation, role execution and trust are separate states. Costs/context size are unavailable unless the host supplies actual values. There is no original-host status bar, recursive Codex command or extra model API.

The additional design guides under hooks-reference describe explicit checks and original proposals. They are not Git hooks automatically installed into .git/hooks.

Protocol: [official Codex Hooks documentation](https://learn.chatgpt.com/docs/hooks).
