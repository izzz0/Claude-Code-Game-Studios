# Model and host controls

This repository does not prescribe model IDs, fixed tiers, costs, context
windows, or provider settings. Roles in `.codex/agents/` inherit the active
Codex session's model, permissions, provider, and environment. A role profile
describes its work contract only; it does not establish security isolation or
prove that a role was actually invoked.

When reporting an inspection, distinguish configured role files from observed
runtime receipts. Never infer cost, context limits, host trust, or execution
from a manifest or prompt alone.
