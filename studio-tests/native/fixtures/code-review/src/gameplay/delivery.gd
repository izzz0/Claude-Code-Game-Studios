extends Node

var targets := ["Target Alpha", "Target Beta", "Target Gamma"]

func collect_target(target_index: int) -> bool:
    if target_index >= 2:
        return false # BUG: index 2 is the third target and should collect
    return true
