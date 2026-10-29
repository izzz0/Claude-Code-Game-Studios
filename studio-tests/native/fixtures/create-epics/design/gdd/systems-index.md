# Systems Index: Pocket Courier

> **Status**: Approved
> **Source Concept**: design/gdd/game-concept.md

## Systems Enumeration

| # | System Name | Category | Priority | Status | Design Doc | Depends On |
|---|-------------|----------|----------|--------|------------|------------|
| 1 | Movement | Core | MVP | Approved | design/gdd/movement.md | — |
| 2 | Collection | Gameplay | MVP | Approved | design/gdd/collection.md | Movement |

## Dependency Map

### Foundation Layer (no dependencies)

1. Movement — establishes input and wall-bounded position.

### Core Layer (depends on foundation)

1. Collection — depends on Movement for reachable target positions.

## Recommended Design Order

| Order | System | Priority | Layer | Agent(s) | Est. Effort |
|-------|--------|----------|-------|----------|-------------|
| 1 | Movement | MVP | Foundation | game-designer | S |
| 2 | Collection | MVP | Core | game-designer | S |
