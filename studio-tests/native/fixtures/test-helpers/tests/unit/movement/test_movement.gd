extends Node

func test_wall_boundary_contract():
    assert(CourierMovement.new().clamp_to_wall(120.0) == 100.0)
