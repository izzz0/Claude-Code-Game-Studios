class_name CourierMovement
extends Node

const WALL_X := 100.0

func clamp_to_wall(position_x: float) -> float:
    return min(position_x, WALL_X)
