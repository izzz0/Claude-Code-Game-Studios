# Movement System

## Summary

- **Layer**: Foundation
- **Priority**: MVP

## Overview

Movement reads horizontal input and clamps the courier against the wall.

## Acceptance Criteria

- Left and right input changes position.
- The courier cannot pass the wall boundary.

## Technical Design

The Godot controller owns horizontal velocity and collision checks.

## Edge Cases

Zero input leaves position unchanged.

## Dependencies

None.
