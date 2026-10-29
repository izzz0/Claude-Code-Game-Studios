extends Node
## Tracks bounded courier health.
signal health_changed(new_value: int)
@export var max_health: int = 100
var health: int = 100
## Applies damage and emits the resulting health.
func take_damage(amount: int) -> void:
    health = clamp(health - amount, 0, max_health)
    health_changed.emit(health)
## Restores health to the configured maximum.
func reset_health() -> void:
    health = max_health
    health_changed.emit(health)
