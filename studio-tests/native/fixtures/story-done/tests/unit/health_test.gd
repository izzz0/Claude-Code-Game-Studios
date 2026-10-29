extends Node

func test_clamp_health_boundaries() -> void:
    assert(HealthRules.clamp_health(-5) == 0)
    assert(HealthRules.clamp_health(100) == 100)
    assert(HealthRules.clamp_health(125) == 100)
