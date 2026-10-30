# physics-domain-expert

# Trait: Physics Domain Expert

> Scope: rigid-body physics, constraints, joints, collision, simulation state, solver stability, physics-to-animation interaction, physics writeback, temporal validation, and physics QA.
>
> This trait complements:
>
> * [`transform-space-expert-trait.md`](./transform-space-expert-trait.md) (Transform Domain)
> * [`blender-animation-domain-expert-trait.md`](./blender-animation-domain-expert-trait.md) (Blender Animation)
> * [`ue5-animation-domain-expert-trait.md`](./ue5-animation-domain-expert-trait.md) (UE5 Animation)
>
> It does **not** replace those traits.

加载时机：触及下文 Activation 所列任一任务时，**MUST** 先读完全文再动手。  
本 trait **只**留在 monospec `traits/`。**MUST NOT** 同步到 `repos/*/traits/` 或子仓业务树。

与 Blender / UE5 / transform traits 同时生效时：本 trait 回答「模拟状态如何行为、如何验收」；引擎 trait 回答「目标系统如何表示」；transform-space-expert 回答「空间与合成」。冲突时，以更严格者为准。涉及 writeback 时 **MUST** 叠加 transform-space-expert 与对应引擎 trait。

---

## 1. Activation

Load this trait when a task involves:

* rigid body
* physics body
* rigid body simulation
* physics solver
* constraint
* joint
* collision
* collision group
* mass
* inertia
* friction
* restitution
* damping
* gravity
* force
* torque
* velocity
* angular velocity
* impulse
* penetration
* constraint error
* physics cache
* physics bake
* substep
* solver iteration
* ragdoll
* physical animation
* physics asset
* Chaos
* Blender Rigid Body
* Blender Rigid Body Constraint
* physics writeback
* rigid body → bone
* bone → rigid body
* physics QA
* physics validation

---

## 2. Core Principle

## Physics State is not Animation State.

Never assume:

```text
Physics Transform == Bone Transform
```

or:

```text
Animation Pose == Physics Pose
```

or:

```text
Physics Body Transform == Constraint Transform
```

These are different semantic states.

The canonical mental model is:

```text
Animation State
       ↓
Physics Input State
       ↓
Physics Solver
       ↓
Physics State
       ↓
Optional Writeback
       ↓
Animation / Bone State
```

Each arrow is a semantic boundary.

---

## 3. Physics Object Model

Treat the following as independent entities:

```text
Physics System
│
├── Rigid Body
│   ├── position
│   ├── rotation
│   ├── linear velocity
│   ├── angular velocity
│   ├── mass
│   ├── inertia
│   └── collision geometry
│
├── Constraint / Joint
│   ├── body A
│   ├── body B
│   ├── anchor
│   ├── axis
│   ├── linear limits
│   ├── angular limits
│   └── motor / drive
│
├── Collision
│   ├── shape
│   ├── layer/group
│   ├── filter
│   └── contact
│
├── Solver
│   ├── timestep
│   ├── substeps
│   ├── iterations
│   └── integration
│
└── Simulation State
    ├── position
    ├── orientation
    ├── velocity
    ├── angular velocity
    ├── contact state
    └── constraint state
```

Do not collapse these into one generic `Transform`.

---

## 4. Physics Transform Semantics

Every physics transform must identify:

```text
Object
Space
Frame
Pivot
Reference
Representation
```

Example:

```text
RigidBody.Transform
```

must answer:

```text
Which rigid body?
World space or local space?
Current simulation frame or initial frame?
Center of mass or geometry origin?
Physics engine representation or target-engine representation?
```

If these cannot be answered, do not modify the transform.

---

## 5. Physics State vs Render State

Physics simulation can produce a state that is independent from the rendered object state.

Therefore:

```text
Physics State
    ↓
Presentation State
```

is a conversion boundary.

A visual mismatch does not automatically mean the solver is wrong.

Possible failure:

```text
Physics State      PASS
       ↓
Transform Mapping FAIL
       ↓
Bone Pose          FAIL
       ↓
Mesh               FAIL
```

Therefore debug physics separately from rendering.

---

## 6. Rigid Body Semantics

A rigid body represents a physical object.

Its state normally includes:

```text
position
orientation
linear velocity
angular velocity
mass
inertia
```

The rigid body may additionally have:

```text
collision shape
center of mass
material properties
sleep state
kinematic/dynamic state
```

Never assume its transform corresponds directly to a bone transform.

---

## 7. Center of Mass

Center of mass and object origin are not necessarily equivalent.

Therefore distinguish:

```text
Object Origin
Center of Mass
Collision Shape Origin
Constraint Anchor
Bone Origin
```

A conversion such as:

```text
RigidBody → Bone
```

must explicitly account for the relevant pivot.

Do not silently assume:

```text
RigidBody.Position == Bone.Position
```

---

## 8. Rotation Semantics

Physics rotations can be represented using:

```text
Quaternion
Matrix
Euler angles
Engine-specific rotation representation
```

Prefer quaternion or native physics representation internally when possible.

Avoid:

```text
Quaternion
    ↓
Euler
    ↓
modify one axis
    ↓
Quaternion
```

unless Euler representation is explicitly part of the semantic contract.

---

## 9. Physics Space Delta

通用 space labeling、composition、conversion and duplicate-conversion rules 由 [`transform-space-expert-trait.md`](./transform-space-expert-trait.md) 定义。Physics-specific work additionally MUST distinguish：

- body local frame；
- center-of-mass frame；
- constraint frame A / B；
- solver world frame；
- kinematic target frame；
- animation writeback target frame。

A transform MUST NOT cross these boundaries without the corresponding body / constraint offset and an explicit conversion point。

---

## 10. Constraint Semantics

A constraint is not merely a transform.

It defines a relationship between physical bodies.

Conceptually:

```text
Body A
   │
   │
Constraint
   │
   │
Body B
```

A constraint can define:

```text
anchor
axis
linear limits
angular limits
drive
motor
stiffness
damping
```

The constraint anchor has its own semantic meaning.

Blender's rigid-body documentation likewise describes constraints as relationships between two rigid bodies, with anchor location/orientation established in their local coordinate systems.

---

## 11. Constraint Space

Never assume constraint limits are expressed in:

```text
World Space
```

without verifying the engine semantics.

Determine:

```text
Constraint Origin
Constraint Orientation
Body A Frame
Body B Frame
Limit Space
```

This is especially important for:

```text
hinge
slider
cone
generic
spring
motor
```

For example, Blender's Hinge constraint uses the constraint object's Z axis as the hinge axis.

Therefore a seemingly correct axis can still be semantically wrong if the constraint frame is wrong.

---

## 12. Constraint Limits

A constraint limit should be treated as a mathematical invariant.

Example:

```text
Angular X:
    min = -30°
    max = +30°
```

means the relative motion must remain within that domain.

Validation should check:

```text
min ≤ current ≤ max
```

with an explicit tolerance.

Do not judge constraint correctness solely from visual appearance.

---

## 13. Constraint Error

Define constraint error explicitly.

For positional constraints:

```text
position_error =
    distance(anchor_A, anchor_B)
```

For rotational constraints:

```text
rotation_error =
    angular_distance(rotation_A, rotation_B)
```

For limited constraints:

```text
limit_violation =
    max(
        min - value,
        0,
        value - max
    )
```

Use domain-appropriate metrics.

---

## 14. Physics Solver Pipeline

The conceptual pipeline is:

```text
Initial State
      ↓
Kinematic / Animation Input
      ↓
Force / Torque
      ↓
Collision Detection
      ↓
Constraint Solving
      ↓
Integration
      ↓
Contact Resolution
      ↓
Updated Physics State
```

The actual engine implementation may differ.

Do not assume solver order without verifying the target engine.

---

## 15. Timestep

Physics behavior depends on simulation timestep.

Always identify:

```text
Frame Rate
Physics Timestep
Substep Count
Solver Iterations
```

Do not compare two physics runs as equivalent if their simulation timing differs without accounting for it.

---

## 16. Substeps

Substeps improve simulation temporal resolution.

Conceptually:

```text
Frame N
   ↓
Substep 1
   ↓
Substep 2
   ↓
Substep 3
   ↓
Frame N+1
```

Do not treat:

```text
1 frame = 1 physics step
```

as universally true.

Blender exposes `Substeps Per Frame` as a rigid-body world setting, and documents that increasing it improves simulation accuracy at higher cost.

---

## 17. Solver Iterations

Constraint solver iterations affect how accurately constraints are satisfied.

Higher iteration counts can improve stability and constraint satisfaction, at computational cost.

Therefore when diagnosing:

```text
constraint drift
joint instability
stack instability
penetration
```

record:

```text
solver iterations
substeps
```

Do not modify these blindly to hide a semantic bug.

---

## 18. Stability vs Correctness

Do not confuse:

```text
Stable
```

with:

```text
Correct
```

A simulation can be:

```text
stable but wrong
```

Example:

```text
incorrect joint axis
+
high damping
=
stable but incorrect motion
```

Likewise:

```text
correct configuration
+
insufficient solver quality
=
unstable simulation
```

Separate:

```text
Semantic Correctness
```

from:

```text
Numerical Stability
```

---

## 19. Energy / Velocity Sanity

Physics outputs should be checked for abnormal values.

Detect:

```text
NaN
Inf
extreme position
extreme velocity
extreme angular velocity
extreme acceleration
```

For each body:

```text
linear_speed
angular_speed
linear_acceleration
angular_acceleration
```

should be available where practical.

---

## 20. Explosive Simulation Detection

Typical physics explosion pattern:

```text
frame N:
    velocity = normal

frame N+1:
    velocity = huge

frame N+2:
    position = extremely far

frame N+3:
    solver diverges
```

Detect:

```text
velocity spike
angular velocity spike
position divergence
constraint error spike
penetration spike
```

Do not wait for the final PNG.

---

## 21. Jitter Detection

Physics jitter is a temporal phenomenon.

Do not classify a single frame as jitter.

Use a window:

```text
N-K ... N ... N+K
```

Measure:

```text
position variance
rotation variance
velocity variance
angular velocity variance
```

A body that should be stationary but continually oscillates can be detected numerically.

---

## 22. Sleeping / Rest State

A body reaching a visually stable pose does not necessarily mean the solver has reached a stable state.

If the engine exposes sleep state, validate:

```text
velocity ≈ 0
angular velocity ≈ 0
sleep state = expected
```

Do not use a fixed visual threshold alone.

---

## 23. Collision Semantics

Collision validation should distinguish:

```text
Expected Contact
Unexpected Contact
Penetration
Missed Contact
Excessive Separation
```

Do not classify every overlap as an error.

For rigid-body physics, some apparent intersections may be expected due to:

```text
collision group
collision mask
body geometry
solver tolerance
```

---

## 24. Collision Filtering

Collision filtering is part of physics semantics.

Validate:

```text
body collision group
collision mask
enabled/disabled state
```

before changing geometry.

A collision problem may be caused by filtering rather than shape placement.

---

## 25. Penetration

Track penetration depth when available.

Example:

```text
max_penetration = 0.003 m
```

should be interpreted against a project-defined tolerance.

Do not use:

```text
penetration > 0
```

as an automatic failure.

Physics engines operate with numerical tolerances.

---

## 26. Contact Stability

A valid contact should not oscillate unpredictably.

Useful signals:

```text
contact count
contact duration
contact position
contact normal
normal impulse
friction impulse
```

when available.

This is particularly useful for:

```text
feet
hands
cloth
hair
skirts
accessories
ragdolls
```

---

## 27. Friction

Friction affects tangential motion.

Do not diagnose sliding only from screenshots.

Measure:

```text
relative tangential velocity
normal force / impulse
friction response
```

when the engine exposes the required data.

---

## 28. Damping

Damping controls energy dissipation.

Do not increase damping merely because a simulation jitters.

First determine whether the actual problem is:

```text
wrong constraint
wrong mass
wrong inertia
wrong collision
wrong timestep
wrong coordinate system
```

Damping can hide symptoms without fixing the root cause.

---

## 29. Mass and Inertia

Mass affects translational response.

Inertia affects rotational response.

Do not treat them as interchangeable.

A body that rotates incorrectly may require investigation of:

```text
inertia
center of mass
rotation frame
constraint axis
```

rather than simply changing mass.

---

## 30. Force vs Impulse

Distinguish:

```text
Force
```

from:

```text
Impulse
```

Force acts over time.

Impulse represents an instantaneous momentum change.

Do not replace one with the other without understanding the intended physical behavior.

---

## 31. Kinematic vs Dynamic

Always distinguish:

```text
Kinematic
```

from:

```text
Dynamic
```

A kinematic body can be driven by animation or explicit motion while participating in physics interactions.

A dynamic body is driven by the physics solver.

Do not assume:

```text
Animation-driven body
=
Physics-driven body
```

Unreal's Chaos documentation also distinguishes kinematic and dynamic simulation states in its physics-field system.

---

## 32. Animation → Physics

When animation drives physics, use an explicit boundary:

```text
Animation Pose
       ↓
Physics Target / Kinematic State
       ↓
Physics Solver
```

Do not silently modify animation bones to compensate for physics errors.

---

## 33. Physics → Animation

When physics drives animation:

```text
Physics State
       ↓
RigidBody → Bone Conversion
       ↓
Bone Pose
```

The conversion is a semantic operation.

It must define:

```text
source frame
target frame
pivot
offset
parent
coordinate conversion
composition order
```

---

## 34. Physics Writeback

Physics writeback must be treated as a separate layer.

```text
Physics Solver
      ↓
Physics State
      ↓
Writeback Conversion
      ↓
Animation/Bone State
```

Never classify:

```text
mesh tearing
```

as a physics-solver failure before checking writeback.

---

## 35. Writeback Failure Classification

Use:

```text
PHYSICS-SOLVER
    solver produced invalid state

PHYSICS-CONFIG
    mass / inertia / collision / constraint configuration

PHYSICS-SPACE
    coordinate-space error

PHYSICS-CONSTRAINT
    incorrect joint frame / limits / anchor

PHYSICS-NUMERIC
    timestep / solver / instability

PHYSICS-WRITEBACK
    physics → animation conversion

PHYSICS-SKIN
    bone → mesh deformation

PHYSICS-VISUAL
    presentation-only discrepancy
```

---

## 36. Never Hide Physics Errors in Writeback

Do not modify:

```text
bone offset
scale
rotation
parent transform
```

just to make a physics result visually match.

First establish:

```text
Physics State Correct?
```

Then:

```text
Writeback Correct?
```

Then:

```text
Skinning Correct?
```

---

## 38. Blender Physics Boundary

Blender rigid-body simulation overrides the effective position/orientation of dynamic rigid-body objects during simulation while the underlying object transform data has its own animation relationship. The Blender manual documents this distinction explicitly.

Therefore when validating Blender physics:

```text
Object Transform
```

and:

```text
Evaluated Physics State
```

must not automatically be treated as identical.

---

## 39. Blender Physics World

When diagnosing Blender rigid-body issues, record:

```text
RigidBodyWorld
Collection
Constraints
Speed
Substeps
Solver Iterations
Cache Range
```

Blender's Rigid Body World owns global simulation settings and the participating rigid-body/constraint collections.

---

## 40. UE5 Chaos Boundary

For UE5:

```text
Animation
       ↓
Skeletal / Physics Representation
       ↓
Chaos
       ↓
Physics State
       ↓
Physical Animation / Rigid Body / Control
```

UE5.8 Chaos supports rigid-body dynamics, constraints, damping, friction, physical animation, ragdoll, and related systems.

Do not assume a Chaos rigid body transform is automatically equivalent to the Skeletal Mesh bone transform.

---

## 41. UE5 Physical Animation

Physical animation combines animation and physics rather than replacing animation completely.

Therefore distinguish:

```text
Animation Target
Physics State
Final Bone Pose
```

UE documents Physical Animation as applying physics simulation on top of Skeletal Mesh animation for selected bone groups.

---

## 42. UE5 Physics Asset

A Physics Asset represents physical bodies and constraints associated with a skeletal mesh.

Do not assume:

```text
Skeleton Bone
=
Physics Body
```

A physics asset may use simplified collision bodies and constraint relationships.

Therefore debugging should identify:

```text
Skeleton Bone
Physics Body
Constraint
```

separately.

---

## 43. UE5 Physics Control

If Physics Control is involved, distinguish:

```text
Control
Body Modifier
Physics State
Final Pose
```

The UE5.8 Physics Control plugin provides controls and body modifiers and includes a rigid-body animation graph node.

Do not treat a control target as the actual solved body state.

---

## 44. Physics Fields

If the system uses external fields:

```text
Field
    ↓
Physics Particle
    ↓
Solver
```

must be considered part of the simulation input.

UE5.8 Physics Fields can directly affect Chaos simulations and can apply effects such as force or velocity to physics objects.

Therefore reproduce field configuration when debugging a physics result.

---

## 45. Determinism

Do not assume physics is deterministic merely because the input file is identical.

Record:

```text
engine version
solver configuration
timestep
substeps
iterations
initial state
random seed if applicable
platform
physics settings
```

When deterministic replay is required, explicitly establish which variables must be fixed.

---

## 46. Reproducibility

A physics bug should ideally be reproducible from:

```text
Input Asset
+
Initial State
+
Simulation Settings
+
Frame Range
```

If possible, save:

```text
physics_state.json
```

containing at minimum:

```text
frame
body
position
rotation
linear_velocity
angular_velocity
sleep_state
```

（原文在本节截断；若后续还有 §47+，可再追加落盘。）

---

## 非目标

- 不替代 [`transform-space-expert-trait.md`](./transform-space-expert-trait.md)、[`blender-animation-domain-expert-trait.md`](./blender-animation-domain-expert-trait.md)、[`ue5-animation-domain-expert-trait.md`](./ue5-animation-domain-expert-trait.md)
- 不替代具体 Graph 的 Gate / 证据包契约（见 [`pipelines-trait.md`](./pipelines-trait.md)）
- 不把本 trait 默认同化进子仓 `traits/`
