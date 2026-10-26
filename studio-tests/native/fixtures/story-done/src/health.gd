class_name HealthRules

static func clamp_health(value: int) -> int:
    return clampi(value, 0, 100)
