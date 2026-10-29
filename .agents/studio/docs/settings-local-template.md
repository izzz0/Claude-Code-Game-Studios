# Local host settings

This template intentionally contains no settings file. Codex permissions,
model selection, provider, and trust are controlled by the host application.
Keep project-specific facts in `project.local.yaml` (ignored) and never commit
credentials, global configuration, or per-file permission policy here.

The repository's `.codex/hooks.json` is a project-local registration reference;
it does not install or enable hooks globally. A configured hook is not evidence
that the host trusted or executed it. Report configured, observed, and
trust-unconfirmed states separately.
