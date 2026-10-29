# Explicit asset validation after integration

This original proposal is not registered as an automatic Git post-merge hook. After an authorized integration, run ccgs-asset-audit on the affected asset roots and actual manifest/contracts. Godot uses assets/, Unity Assets/, and Unreal Content/.

Native PostToolUse checks cover actual supported file edits and report invalid data JSON or applicable naming concerns. Size budgets, imports and runtime correctness require their actual engine/tool reports. The adapter does not merge branches or mutate assets.
