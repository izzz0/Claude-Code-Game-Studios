# Native hook input and output

The [official Codex Hooks protocol](https://learn.chatgpt.com/docs/hooks) is authoritative. Input is one JSON object on stdin. Common fields include session_id, cwd and hook_event_name; turn_id and actual agent/tool identities are event-specific.

Native unified shell calls are reported as tool_name Bash with tool_input.command. Native file patches are apply_patch with the patch in tool_input.command. Inspect every Add File, Update File, Delete File and Move to header; paths are relative to event cwd. Compatibility Write/Edit payloads use file_path and content or old_string/new_string.

PreToolUse can deny with exit 0 and JSON hookSpecificOutput containing hookEventName PreToolUse, permissionDecision deny and permissionDecisionReason. Alternatively exit 2 with the reason on stderr. Do not print denial JSON and then exit 2.

SessionStart, SubagentStart, PreToolUse and PostToolUse support their event-specific additionalContext. PreCompact/PostCompact use common JSON output fields; do not invent an additionalContext event shape for them. PostToolUse feedback cannot undo a completed write.

Stop/SubagentStop require JSON on successful exit; this adapter emits systemMessage only and never requests continuation. Interrupt and SessionEnd are observational and cannot restart a turn. Their configured timeouts are at most three seconds.

Hook failure is not a game-test result. Native events are distinct from protocol fixture executions. write_stdin does not run a fresh pre-tool hook, and specialized host tools may have incomplete coverage. Do not describe these checks as a security sandbox.
