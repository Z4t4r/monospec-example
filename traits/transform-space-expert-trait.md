# Transform & Animation Domain Expert Trait

> Scope: Blender / UE5 animation, skeletal transform,
> rigid-body physics, IK, animation evaluation, and physics writeback.
>
> Purpose: Prevent mathematically valid but semantically incorrect
> transform implementations.

加载时机：触及下文 Activation 所列任一任务时 **MUST** 先读完全文再动手。  
本 trait **只**留在 monospec `traits/`。**MUST NOT** 同步到 `repos/*/traits/` 或子仓业务树。

文件名：`transform-space-expert-trait.md`（索引键不变）。

---

## 1. Activation

This Trait MUST be applied whenever a task:

* reads, writes, converts, or composes a Bone Transform;
* reads, writes, converts, or composes a RigidBody Transform;
* modifies skeletal animation evaluation;
* modifies physics-to-bone writeback;
* modifies IK / constraint solving;
* modifies parent-child transform propagation;
* modifies local / component / world transform conversion;
* modifies Blender / UE coordinate conversion;
* modifies quaternion / Euler / rotation-order handling;
* modifies `bone_offset`, pivot, inverse bind, rest pose, or bind pose;
* modifies animation sampling or interpolation;
* modifies the final evaluated pose;
* modifies code responsible for Blender ↔ UE transform conversion.

Typical affected concepts include:

```text
Bone
PoseBone
EditBone
Armature
RigidBody
Constraint
IK
Parent
Rest Pose
Bind Pose
Local Transform
Component Transform
World Transform
Bone Matrix
RigidBody Matrix
bone_offset
Inverse Bind
Quaternion
Euler
Rotation Order
Coordinate Conversion
Physics Writeback
```

If uncertain whether this Trait applies, assume that it DOES.

---

## 2. Core Principle

## Mathematical validity does not imply semantic correctness.

A transform operation can be mathematically valid while being
wrong for the animation domain.

Example:

```text
R * BoneMatrix
```

is mathematically valid.

It is NOT automatically valid to interpret this as:

```text
"Apply coordinate conversion R to this bone."
```

Before applying a transform, determine:

```text
WHAT
    is being transformed?

FROM
    which coordinate space?

TO
    which coordinate space?

RELATIVE TO
    which parent / pivot / basis?

WITH
    which semantic offset?

IN WHAT ORDER
    are transforms composed?
```

Never use matrix algebra alone as proof of semantic correctness.

---

## 3. Transform Contract

Every non-trivial transform conversion MUST have an explicit
Transform Contract.

The Agent MUST be able to identify:

```text
Source Object
Source Space
Source Representation

Target Object
Target Space
Target Representation

Parent Space
Pivot / Origin
Rest / Bind Pose
Semantic Offset
Coordinate Conversion
Composition Order
```

Example:

```text
Source Object:
    Physics RigidBody

Source Space:
    RigidBody local / world

Source Representation:
    RigidBody Transform

Target Object:
    Blender PoseBone

Target Space:
    Pose / parent-relative

Target Representation:
    PoseBone rotation + location

Parent Space:
    Blender parent bone

Pivot:
    Bone / rigid-body relationship

Semantic Offset:
    bone_offset

Coordinate Conversion:
    XZY

Composition Order:
    Explicitly defined
```

If these fields cannot be determined, the Agent MUST investigate
the surrounding code before modifying transform mathematics.

---

## 4. Semantic Object Distinction

The following objects MUST NOT be treated as interchangeable:

```text
Blender EditBone
Blender Bone
Blender PoseBone
Blender Armature Object
Physics Body
Physics Constraint
UE Bone
UE Component Transform
UE World Transform
```

In particular:

```text
RigidBody Transform != Bone Transform
Bone Matrix != PoseBone Transform
Pose Transform != World Transform
Rest Pose != Evaluated Pose
Animation Transform != Physics Transform
Physics Transform != Skinning Transform
```

A conversion between these objects MUST be explicit.

---

## 5. Space Discipline

Every transform variable SHOULD make its space obvious.

Prefer names such as:

```text
local_transform
parent_transform
component_transform
world_transform
rigidbody_world
rigidbody_local
bone_local
bone_component
bone_world
pose_transform
rest_transform
```

Avoid ambiguous names such as:

```text
transform
matrix
rotation
position
bone_matrix
```

when the surrounding code contains multiple coordinate spaces.

If an existing variable has an ambiguous name, the Agent MUST inspect
its construction and consumers before changing its meaning.

---

## 6. Local / Parent / Component / World

Never assume that:

```text
Local == Component
Component == World
Bone == World
RigidBody == Bone
```

For hierarchical transforms:

```text
ChildWorld
    =
ParentWorld
    *
ChildLocal
```

The exact convention used by the project MUST be verified before
implementing or changing this relationship.

Do not introduce a mathematically equivalent-looking alternative
without checking the project's existing convention.

---

## 7. Matrix Composition Order

Matrix multiplication order MUST be treated as semantic information.

These are NOT interchangeable:

```text
A * B
B * A
```

The Agent MUST determine:

```text
What space does A operate in?
What space does B operate in?
Is A a basis conversion?
Is A a parent transform?
Is A an offset?
Is B already composed?
```

Never select multiplication order solely because it produces a
visually plausible result in one frame.

---

## 8. Coordinate-System Conversion

Coordinate conversion MUST be applied at the semantic boundary
where the source representation is converted to the target
representation.

Preferred conceptual pipeline:

```text
Source Transform
        │
        ▼
Source-space interpretation
        │
        ▼
Coordinate conversion
        │
        ▼
Semantic offset / pivot correction
        │
        ▼
Target local transform
        │
        ▼
Parent hierarchy composition
        │
        ▼
Target evaluated transform
```

Do NOT blindly use:

```text
CoordinateConversion * FinalBoneMatrix
```

unless the project's transform contract explicitly proves that this
is the correct operation.

---

## 9. Coordinate Conversion Must Not Be Duplicated

Before introducing:

```text
XZY
XYZ
YZX
axis swap
basis conversion
quaternion conversion
Euler conversion
```

the Agent MUST search for existing project-level conversion logic.

Check:

```text
Import
Export
Animation evaluation
Physics solver
Bone conversion
RigidBody conversion
Writeback
Rendering
Utility math
```

The same coordinate conversion MUST NOT be applied twice merely
because the intermediate representation appears to require it.

Typical failure:

```text
Source → XZY
       ↓
Bone conversion
       ↓
XZY again
       ↓
Incorrect pose
```

---

## 10. Offset Semantics

Existing offsets MUST be treated as semantic invariants until proven
otherwise.

Examples:

```text
bone_offset
pivot_offset
rest_offset
bind_offset
rigidbody_offset
constraint_offset
inverse_bind
```

Never remove, bypass, duplicate, or relocate an offset without
determining:

```text
Why does it exist?
Which coordinate space does it belong to?
Which object relationship does it encode?
At which stage is it applied?
```

A seemingly redundant offset may encode a necessary relationship
between two different coordinate systems.

---

## 11. Bone Offset Rule

If the project contains a known `bone_offset` relationship, the Agent
MUST NOT replace:

```text
RigidBody
    ↓
bone matrix
```

with:

```text
RigidBody
    ↓
global rotation
    ↓
bone matrix
```

without proving that `bone_offset` is already represented in the
input matrix.

The Agent MUST explicitly establish whether the intended pipeline is:

```text
RigidBody
    ↓
coordinate conversion
    ↓
bone_offset
    ↓
PoseBone
```

or another project-defined equivalent.

Do not infer this from variable names alone.

---

## 12. Rest Pose / Bind Pose / Evaluated Pose

These states MUST remain conceptually separate:

```text
Rest Pose
Bind Pose
Animation Pose
Physics Pose
Evaluated Pose
```

Never modify the rest/bind structure merely to make an evaluated
animation pose appear correct.

In particular, a runtime physics writeback SHOULD normally affect
the evaluated pose rather than silently redefining the skeletal
rest structure.

If rest/bind data is modified, the Agent MUST identify the reason
and downstream consequences.

---

## 13. Blender-Specific Discipline

When working with Blender:

```text
EditBone
Bone
PoseBone
Armature Object
```

MUST be treated as different layers.

The Agent MUST determine which layer a change belongs to.

Do not use an EditBone/rest-pose operation when the intended change
is an evaluated animation pose.

Do not assume that changing a Bone object's matrix is equivalent to
changing the PoseBone's evaluated transform.

Before modifying Blender writeback code, inspect:

```text
armature mode
bone hierarchy
rest pose
pose state
parent relationship
bone matrix semantics
bone_offset
constraint evaluation
dependency graph evaluation
```

---

## 14. Physics Boundary

This trait owns the transform interface between simulated state and an animation target; [`physics-domain-expert-trait.md`](./physics-domain-expert-trait.md) owns solver、rigid-body、constraint、collision and physical-state semantics.

At writeback, the Agent MUST identify source body frame、target bone / component frame、offset、parent relationship and evaluation stage. It MUST NOT copy a world-space physics transform directly into a local animation channel or diagnose solver correctness from the final mesh alone.

Engine-specific writeback belongs to the applicable Blender or UE5 trait. This section does not redefine those domain rules.

---

## 15. Skinning Is a Separate Layer

The following must be distinguished:

```text
Solver Correctness
Transform Conversion Correctness
Armature Pose Correctness
Skinning Correctness
Rendering Correctness
```

A mesh tear may indicate:

```text
incorrect bone transform
incorrect bind relationship
incorrect skinning matrix
incorrect rest pose
incorrect writeback
```

It does not automatically prove:

```text
physics solver failure
```

---

## 16. Quaternion / Euler Discipline

Never convert between Euler and quaternion merely to make an API
accept the expected type.

Before changing rotation representation, determine:

```text
rotation order
coordinate basis
intrinsic vs extrinsic interpretation
local vs world rotation
normalization requirement
interpolation behavior
```

Do not assume:

```text
Euler XYZ
Euler XZY
Quaternion XYZ
Quaternion XZY
```

are interchangeable representations of the same operation.

Euler order MUST be treated as semantic information.

---

## 17. Avoid Global Euler Operations on Composed Bone Matrices

This is a high-risk operation:

```text
BoneMatrix = XZY * BoneMatrix
```

The Agent MUST flag it for review when the intention is coordinate
conversion.

Before accepting such an operation, prove:

```text
1. BoneMatrix's current space
2. XZY's source space
3. XZY's target space
4. multiplication convention
5. pivot
6. parent relationship
7. bone_offset relationship
8. whether conversion already occurred
```

If these cannot be established, do not treat the operation as safe.

---

## 18. Existing Implementation Is Evidence

When changing transform mathematics, inspect the existing pipeline
before inventing a new formula.

Search for:

```text
same source object
same target object
same conversion
same offset
same matrix type
same rotation order
same writeback path
```

Existing working code is evidence of project-specific semantics.

However:

```text
Existing code != automatically correct
```

The Agent should verify behavior using known poses and numerical
comparisons before copying a pattern into another layer.

---

## 19. Do Not Generalize from One Working Frame

A transform implementation that works in:

```text
T-pose
Frame 0
identity rotation
symmetrical pose
```

is NOT sufficient evidence.

Validation MUST include cases with:

```text
large rotation
non-zero parent rotation
deep hierarchy
asymmetric pose
physics displacement
large translation
combined rotation + translation
```

---

## 20. Golden Pose Requirement

Transform changes SHOULD have at least one deterministic Golden Pose.

A Golden Pose SHOULD contain:

```text
frame
bone
expected local transform
expected component transform
expected rotation
expected position
```

For physics:

```text
frame
rigid body
expected position
expected rotation
expected velocity
```

Golden values SHOULD be numerical whenever practical.

PNG output may be included as supporting evidence, but MUST NOT be
the sole proof of transform correctness.

---

## 21. Regression Test Requirement

Any bug involving:

```text
rotation
coordinate conversion
bone_offset
parent hierarchy
physics writeback
matrix multiplication
```

SHOULD produce a regression test.

The test MUST fail if the original semantic error returns.

Example:

```text
Input:
    Known rigid-body transform

Expected:
    Known evaluated bone transform

Assertion:
    angular error < threshold
    positional error < threshold
```

For the specific class of bug:

```text
RigidBody
    ↓
XZY
    ↓
bone_offset
    ↓
Bone Pose
```

the test SHOULD explicitly distinguish it from:

```text
RigidBody
    ↓
Bone Matrix
    ↓
Global XZY
```

---

## 22. Numerical Validation

For transform changes, prefer numerical evidence over screenshots.

At minimum compare:

```text
Position Error
Rotation Error
Scale Error
```

For animation:

```text
Frame-to-frame Position Delta
Frame-to-frame Rotation Delta
Velocity
Angular Velocity
Acceleration
Angular Acceleration
```

For hierarchy:

```text
Parent Transform
Child Local Transform
Child Component Transform
```

For physics:

```text
RigidBody Position
RigidBody Rotation
Linear Velocity
Angular Velocity
Constraint Error
Penetration
```

---

## 23. Rotation Error

When comparing rotations, avoid naive Euler subtraction when possible.

Prefer a quaternion or relative-rotation based metric.

Conceptually:

```text
R_error = inverse(R_expected) * R_actual
```

Then evaluate the angular magnitude of `R_error`.

Do not conclude that two rotations are equivalent merely because
their Euler components appear numerically similar.

---

## 24. Temporal Validation

Animation correctness is not only a per-frame property.

A transform can be individually valid while the animation is
temporally incorrect.

Check for:

```text
position spikes
rotation spikes
velocity discontinuities
angular velocity spikes
jitter
unexpected reversal
IK flipping
physics explosion
penetration
constraint instability
```

For detected anomalies, inspect neighboring frames:

```text
Frame N-K
...
Frame N
...
Frame N+K
```

---

## 25. Sampling Strategy

Do not rely exclusively on:

```text
Frame 0
Frame 25
Frame 50
Frame 75
Frame 100
```

Prefer:

```text
Uniform baseline samples
        +
High-motion samples
        +
Detected anomaly neighborhoods
        +
Key event frames
```

This is especially important for physics and IK.

A five-frame screenshot sample may miss a one-frame instability.

---

## 26. AI Validation Boundary

AI is useful for semantic anomalies that are difficult to encode
as simple numerical rules.

Examples:

```text
hand points in an implausible direction
knee bends backward
left/right limb semantic mismatch
IK appears to flip
foot contact is inconsistent
pose does not match the intended action
```

AI MUST NOT be treated as the sole authority for:

```text
matrix correctness
coordinate conversion correctness
quaternion correctness
exact bone transform correctness
physics numerical stability
```

These should be validated numerically where possible.

---

## 27. Semantic Pose Representation

When AI needs to inspect a pose, prefer a semantic representation
over raw matrices or raw quaternion dumps.

Example:

```text
FRAME 128

Root:
    motion = forward
    velocity = 4.2 m/s

Pelvis:
    height = 0.91 m
    pitch = -4°
    yaw = 2°

LeftLeg:
    thigh_flexion = 42°
    knee_flexion = 87°
    foot_contact = true

RightLeg:
    thigh_flexion = 39°
    knee_flexion = 84°
    foot_contact = true
```

This allows an Agent to reason about:

```text
pose semantics
joint relationships
motion semantics
symmetry
contact
```

without requiring it to infer domain meaning from raw matrices.

---

## 28. AI Must Not Invent Domain Semantics

If the Agent encounters an unfamiliar field such as:

```text
bone_offset
hybrid_bc
hierarchical
physics_solved
```

it MUST inspect:

```text
definition
producer
consumer
call sites
data structure
documentation
tests
```

before assigning semantic meaning.

Variable names are hints, not proof.

---

## 29. Transform Debugging Protocol

When a transform bug is suspected, follow this order.

### Step 1 — Identify the symptom

Example:

```text
Bone rotation differs by ~1.4 rad
```

### Step 2 — Capture intermediate states

```text
Input Transform
Converted Transform
Offset-applied Transform
Parent-composed Transform
Final Pose Transform
```

### Step 3 — Label every state

For each state:

```text
Object
Space
Parent
Pivot
Rotation representation
```

### Step 4 — Compare numerical differences

Determine where the first unexpected difference occurs.

### Step 5 — Locate the semantic boundary

Find the first operation where:

```text
source semantics
```

become:

```text
target semantics
```

### Step 6 — Check for duplicate conversion

Especially:

```text
axis conversion
rotation conversion
offset
parent composition
```

### Step 7 — Verify with a Golden Pose

Do not rely on visual inspection alone.

---

## 30. Transform Change Protocol

Before modifying transform code, the Agent SHOULD produce internally
a short reasoning record:

```text
Source:
Target:
Source Space:
Target Space:
Parent Space:
Pivot:
Existing Offset:
Coordinate Conversion:
Composition Order:
Expected Invariant:
Validation:
```

Only after these are understood should the code be changed.

For high-risk changes, this information SHOULD be included in the
implementation notes or PR description.

---

## 31. High-Risk Operations

The following operations MUST trigger additional review:

```text
matrix multiplication
matrix inversion
quaternion multiplication
Euler conversion
rotation-order changes
coordinate-system conversion
bone_offset changes
parent transform changes
rest-pose modification
inverse-bind modification
physics writeback
IK transform writeback
world → local conversion
local → world conversion
```

Especially high risk:

```text
R * ExistingBoneMatrix
ExistingBoneMatrix * R
Inverse * Transform
Transform * Inverse
```

The Agent MUST explain the space semantics before accepting these
operations.

---

## 32. Forbidden Shortcuts

The Agent MUST NOT use these reasoning shortcuts:

```text
"It looks right in the screenshot."

"The matrix multiplication is mathematically valid."

"The variable is called bone_matrix, so it must be a bone-local matrix."

"XZY is the correct conversion, so apply XZY here."

"RigidBody rotation should equal Bone rotation."

"The existing mesh tear means physics is broken."

"Frame 0 looks correct, therefore the animation is correct."

"The result is visually close enough."

"The engine accepts this transform, therefore the
semantics are correct."
```

---

## 非目标

- 不替代具体 Graph 的 Gate / 证据包契约（见 [`pipelines-trait.md`](./pipelines-trait.md)）
- 不规定某条 Graph 的 Socket 字段名；只约束 transform / animation 语义与验收方式
- 不把本 trait 默认同化进子仓 `traits/`
