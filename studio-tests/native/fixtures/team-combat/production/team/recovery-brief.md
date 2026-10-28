# Synthetic team recovery input

This fixture asks the coordinator to exercise recovery, not to trust a prior record. After native role assignment, one real implementation task must be deliberately marked interrupted or failed using its returned task and agent IDs, then resumed with `team-run.py resume` and verified from the returned state. No task or agent ID is supplied here.

Use Cocos/TypeScript applicable roles only; this is a recovery request, never pre-existing evidence.
