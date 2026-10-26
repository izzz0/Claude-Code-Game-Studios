# Collection System

## Summary

- **Layer**: Core
- **Priority**: MVP

## Overview

Collection records three target pickups reached by the moving courier.

## Acceptance Criteria

- Each target increments the count once.
- Completion is signaled at exactly three collected targets.

## Technical Design

Targets emit a collection event consumed by the run state.

## Edge Cases

A collected target cannot increment twice.

## Dependencies

Movement.
