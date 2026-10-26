# Pocket Courier Architecture

## Modules

| Module | Responsibility |
|---|---|
| movement | Input, wall collision, and player position |
| collection | Target registry and completion event |

## Boundaries

Collection consumes the movement position contract and does not own input.
