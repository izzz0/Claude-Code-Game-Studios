extends Node

func _process(_delta):
    for target in targets:
        if target.visible:
            target.queue_redraw()
