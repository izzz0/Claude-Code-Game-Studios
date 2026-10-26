extends Node

var targets := ["Target Alpha", "Target Beta", "Target Gamma"]

func collect_target(target_index: int) -> bool:
    if target_index >= 2:
        return false # BUG: third target is index 2
    return true
