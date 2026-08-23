---
name: game-development
description: Route broad game-development design work to the relevant platform or discipline guidance. Use for greenfield direction or cross-cutting game questions; do not trigger for a repository-specific bug, compiler/runtime work, emulator validation, or an implementation task whose platform and contract are already established.
---

# Game development router

Route only the part of the request that benefits from general game-development
guidance. Existing repository architecture, platform constraints, measured
behavior, and acceptance artifacts outrank generic patterns.

## Existing projects

Before applying a platform skill:

1. Read the project's instructions, design documents, target constraints, and
   relevant code.
2. Identify the actual engine/runtime, hardware budget, update model, input
   semantics, asset pipeline, and validation surface.
3. Use the matching subskill only for a decision not already answered by those
   sources.

For a concrete bug or regression, reproduce it through the real game/runtime
path instead of routing to generic design guidance. For compiler, emulator, ROM,
or platform-lowering work, use the repository's exact acceptance surface.

## Route by need

- Browser runtime or PWA constraints: `web-games`
- Mobile input, battery, or store constraints: `mobile-games`
- PC or console platform integration: `pc-games`
- 2D rendering, tilemaps, physics, or camera: `2d-games`
- 3D rendering, shaders, physics, or camera: `3d-games`
- Game rules, progression, balance, or player experience: `game-design`
- Networking and synchronization: `multiplayer`
- Art direction and asset pipeline: `game-art`
- Sound design and adaptive audio: `game-audio`

Load the minimum relevant set. A 2D game does not automatically need every 2D,
platform, design, art, and audio reference.

## Evidence discipline

- Measure before assigning performance budgets or recommending optimization.
- Verify engine, hardware, certification, pricing, and platform facts from
  current primary sources when they matter.
- Prefer the project's established input and timing contracts over generic
  fixed-timestep or action-mapping advice.
- Recommend architectural patterns only for a demonstrated need; do not add
  pooling, ECS, events, or abstraction by default.
- Validate changes in the real target runtime when build/tests cannot establish
  playability, visuals, timing, audio, or hardware behavior.

## Completion

The routing is complete when the selected guidance addresses the unresolved
decision without replacing repository-specific evidence with generic game
development lore.
