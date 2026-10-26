extends Node

# TODO: cache the target lookup instead of allocating a string every frame.
func update_target_label(target_id: int) -> void:
    var label_key := "target_" + str(target_id)
    print(label_key)
