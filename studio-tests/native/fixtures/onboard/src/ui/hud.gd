extends CanvasLayer

@onready var combo_label: Label = $ComboLabel

func show_parcel_combo(count: int) -> void:
	combo_label.text = "Parcel combo x" + str(count)
