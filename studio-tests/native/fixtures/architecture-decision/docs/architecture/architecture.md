# Architecture

## Layer Map

The layer vocabulary is Foundation, Core, Feature, and Presentation.

### Foundation Layer

- None defined in this fixture.

### Core Layer

- None defined in this fixture.

### Feature Layer

- **DeliveryService** (Gameplay Domain; delivery-state ownership): owns delivery state and emits `delivery-recorded`. Scene adapters call it; persistence does not own delivery state.

### Presentation Layer

- None defined in this fixture.
