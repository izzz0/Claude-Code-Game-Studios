# Native coordination contract

Use project-native profiles in .codex/agents, named ccgs-<source-role>. They inherit the parent's selected model, permissions and provider. Do not copy source-host tools/model/maxTurns declarations or pretend prompts establish security isolation.

A team skill selects its active roles from team.size and the actual task. The coordinator uses native subagent tools, waits for required results, and records real agent/run identity, assignment, owned files, output paths, findings and next action. When a host cannot spawn the named role, report NOT ASSESSED; do not describe an invented consultation.

Use scripts/team-run.py to retain the orchestration manifest. Registration/receipts are observations, not attestations: the coordinator must validate returned artifact existence, freshness and substance. Pending/failed/interrupted work cannot be marked done by writing a filename. Bound concurrency to the host and serialize dependent work. Assign one writer per file; independent reviewers read only.

`team-run.py init --id` is a local record slug (for example `chase-capture-01`), not a native coordinator identity. The current agent coordinates directly; do not spawn a child merely to obtain that label. Record each actual host-returned child UUID or exact unambiguous agent path (for example `/root/chase_designer`) in `event --agent-id`; keep run/task slugs separate from those identities. Never remove path separators from an agent identity or invent a UUID.

Configured independent review needs a separate reviewer run that did not implement that change. Keep reviewer identity and hashes. The coordinator may retain the review response after the read-only phase; the reviewer does not create a stamp or change a checkpoint. If independence is required and unavailable, stop at NOT ASSESSED. Self-review is explicit and only applicable where the route allows it.

Review_mode solo skips director panels; lean runs phase gates; full runs the applicable specialist/director gates. Workflow defines the documents to evaluate, while team.size defines active production roles. Do not conflate these axes.

On interruption retain assignments, artifacts, actual files and remaining checks. On recovery compare working branch and current files with saved facts, reconcile any dead agent runs, and spawn a fresh attempt when required. Old identity or partial output is not a successful result.

Project/QA artifacts and checkpoint writes belong to the coordinator's authorized skill phase. Runtime hooks write only isolated ignored observational receipts. Plans, status queries and code reviews leave code, stories, QA evidence and checkpoints unchanged. Never use a Stop callback to complete unrelated backlog or repeatedly restart a cancelled turn.
