# blender-animation-domain-expert

# Trait: Blender Animation Domain Expert

> Scope: Blender Armature, Bone, PoseBone, animation evaluation,
> constraints, IK, physics writeback, and transform conversion.
>
> Purpose: Prevent AI Agents from applying generic transform logic
> to Blender animation data incorrectly.

加载时机：触及下文 Activation 所列任一任务，或改动会影响 Armature 最终 pose 时，**MUST** 先读完全文再动手。  
本 trait **只**留在 monospec `traits/`。**MUST NOT** 同步到 `repos/*/traits/` 或子仓业务树。

与 [`transform-space-expert-trait.md`](./transform-space-expert-trait.md) 同时生效时：通用 transform 语义由该 trait 约束；本 trait 约束 Blender 层（EditBone / Bone / PoseBone / evaluation）的边界。冲突时，以更严格者为准。  
与 [`python-dialect-trait.md`](./python-dialect-trait.md) 同时生效时：方言决定落点；本 trait 决定 Blender 动画语义。

---

## 1. Activation

This Trait MUST be loaded when a task involves:

* Blender Armature
* `bpy.types.Bone`
* `bpy.types.PoseBone`
* `EditBone`
* `matrix`
* `matrix_local`
* `matrix_basis`
* `matrix_channel`
* animation keyframes
* pose evaluation
* constraints
* IK
* physics writeback
* rigid-body → bone conversion
* bone offsets
* rest pose / bind pose
* evaluated pose
* dependency graph evaluation
* Blender animation export

If a change affects the final pose of an Armature, assume this Trait applies.

---

## 2. Blender Bone Layers Are Different

Never treat these as interchangeable:

```text
EditBone
Bone
PoseBone
Armature Object
```

Conceptually:

```text
EditBone
    │
    │ defines / edits structure
    ▼
Rest Bone
    │
    ▼
PoseBone
    │
    ├── Animation
    ├── Constraints
    ├── IK
    └── Drivers
    │
    ▼
Evaluated Pose
    │
    ▼
Deformation / Skinning
```

Blender's own documentation distinguishes the pose-bone layer as the
location where animation transformations, constraints, and IK settings
are applied.

---

## 3. Rest Structure vs Animation Pose

The following are different concepts:

```text
Rest Pose
Bind Pose
Bone Structure
Animation Pose
Evaluated Pose
```

Do NOT modify the rest structure to solve an animation-pose problem.

In particular:

```text
Wrong:
Physics Writeback
    ↓
modify Bone.matrix_local
```

unless the task explicitly intends to modify the rest structure.

For normal animation evaluation/writeback, investigate the
`PoseBone` layer first.

---

## 4. Bone vs PoseBone

`Bone` describes the armature's structural/rest relationship.

`PoseBone` represents the animated pose channel.

Do not assume:

```text
Bone.matrix_local
==
PoseBone.matrix
```

They represent different stages of the Blender animation system.

Blender documents `Bone.matrix_local` as the bone matrix relative to
the armature, while `PoseBone.matrix` is the final pose matrix in
armature object space.

---

## 5. PoseBone.matrix

Treat:

```text
PoseBone.matrix
```

as an **evaluated pose-space result**, not simply as an arbitrary
local bone matrix.

Blender documents it as:

```text
final 4×4 matrix
after constraints and drivers
in armature object space
```

Therefore:

```text
PoseBone.matrix
```

MUST NOT automatically be interpreted as:

```text
bone-local transform
```

without conversion.

---

## 6. PoseBone.matrix_basis

Treat:

```text
PoseBone.matrix_basis
```

as a different semantic layer.

Blender documents it as the location/scale/rotation relative to:

```text
parent
+
own rest bone
```

Therefore:

```text
matrix_basis
```

and:

```text
matrix
```

MUST NOT be substituted for each other simply because both are 4×4
matrices.

---

## 7. Matrix Channel

`PoseBone.matrix_channel` represents another stage of Blender's
pose evaluation and includes animation/drivers and the effect of
bone constraints.

Therefore, when debugging a pose discrepancy, identify whether the
value comes from:

```text
matrix_basis
matrix_channel
matrix
```

Do not treat them as three names for the same transform.

---

## 8. Blender Transform Contract

Before modifying a Blender transform, identify:

```text
Object:
    Armature Object / Bone / PoseBone

Stage:
    Rest / Animation / Constraint / Evaluated

Input Space:
    ?

Output Space:
    ?

Parent:
    ?

Rest Matrix:
    ?

Pose Matrix:
    ?

Offset:
    ?

Coordinate Conversion:
    ?

Composition Order:
    ?
```

If any of these are unknown, inspect the existing implementation
before changing the transform equation.

---

## 9. Parent Hierarchy

Blender bone transforms are hierarchical.

Never assume:

```text
child.matrix
=
child.local_transform
```

without accounting for:

```text
parent pose
parent rest relationship
child rest relationship
```

For conversions between local and pose spaces, prefer Blender's
existing bone conversion facilities when applicable rather than
inventing a second hierarchy formula.

Blender provides `Bone.convert_local_to_pose()` specifically for
conversion between local and pose spaces, including parent pose/rest
matrices.

---

## 10. Prefer Blender's Native Space Conversion

When a task requires:

```text
Local → Pose
Pose → Local
```

first inspect:

```text
Bone.convert_local_to_pose()
```

and the existing project usage.

Do not immediately write:

```text
parent_inverse @ matrix
```

or:

```text
parent_matrix @ matrix
```

unless the exact Blender space semantics have been established.

Blender's API explicitly supports Local ↔ Pose conversion with rest
and parent matrices.

---

## 11. Never Apply Global Rotation Blindly

High-risk example:

```text
pose_bone.matrix =
    XZY @ pose_bone.matrix
```

This MUST trigger investigation.

Determine:

```text
What space is pose_bone.matrix in?
What space is XZY defined in?
Is XZY a basis conversion?
Is XZY already applied upstream?
Does bone_offset belong before or after this conversion?
Does the parent relationship require local conversion?
```

A mathematically valid matrix operation is not proof of Blender
semantic correctness.

---

## 13. bone_offset

If the project contains:

```text
bone_offset
```

treat it as a domain invariant.

Before changing its application point, determine:

```text
source space
target space
pivot
rest relationship
parent relationship
whether it has already been applied
```

Never remove it because the result appears visually similar.

Never add it again because a transform appears visually incorrect.

---

## 14. Coordinate Conversion

Coordinate-system conversion MUST happen at a clearly defined
semantic boundary.

Example:

```text
RigidBody Space
    ↓
Source Coordinate Conversion
    ↓
Blender Bone Semantic Conversion
    ↓
Pose Space
```

Do not silently perform:

```text
Source → Blender conversion
```

in multiple layers.

Search the call chain before adding another:

```text
axis swap
Euler reorder
quaternion conversion
basis rotation
```

---

## 15. Euler Rotation Order

Blender rotation order is part of the transform semantics.

Never assume:

```text
XYZ
XZY
YXZ
YZX
ZXY
ZYX
```

are interchangeable.

When changing Euler handling, verify:

```text
rotation_mode
source Euler order
target Euler order
coordinate basis
intrinsic/extrinsic interpretation
```

If quaternion representation is used, do not assume that converting
Euler → Quaternion automatically preserves the intended semantic
operation if the source order or coordinate basis is wrong.

---

## 16. Quaternion Discipline

When using:

```text
rotation_quaternion
```

verify:

```text
source space
target space
multiplication order
normalization
parent relationship
```

Do not fix an Euler-order bug by arbitrarily replacing Euler
operations with quaternion multiplication.

Quaternions remove Euler singularities; they do not remove
coordinate-space errors.

---

## 17. Constraints and IK

When a PoseBone has:

```text
IK
Constraint
Driver
```

the Agent MUST determine whether the modified transform is:

```text
input to evaluation
```

or:

```text
output of evaluation
```

Do not write an evaluated result back into an upstream control layer
without understanding the evaluation chain.

Potential failure:

```text
Animation
   ↓
IK
   ↓
Evaluated Pose
   ↓
write result
   ↓
IK evaluates again
   ↓
double transformation
```

---

## 18. Physics Writeback

Physics writeback MUST be treated as a separate stage.

Recommended conceptual model:

```text
Animation Pose
       │
       ├───────────────┐
       ▼               ▼
  Bone Evaluation   Physics Solver
       │               │
       │               ▼
       │          Physics State
       │               │
       │               ▼
       │       Transform Conversion
       │               │
       └───────┬───────┘
               ▼
         Final PoseBone
```

Do not assume that a physics body's transform can be assigned
directly to a PoseBone.

---

## 19. Physics Debugging

When physics writeback is wrong, capture:

```text
A = Physics Solver Output
B = Converted Transform
C = PoseBone Input
D = PoseBone Evaluated Matrix
E = Mesh Deformation
```

Then determine the first stage where the error appears.

```text
A wrong
    → Physics Solver / Physics Input

A correct, B wrong
    → Transform Conversion

B correct, C wrong
    → Writeback

C correct, D wrong
    → Blender Evaluation / Constraints / Hierarchy

D correct, E wrong
    → Skinning / Bind / Mesh
```

Do not debug all layers simultaneously.

---

## 20. Mesh Tearing Classification

A mesh tear MUST NOT immediately be classified as:

```text
Physics Solver Error
```

Possible causes include:

```text
Transform Conversion
Wrong Pose Space
Wrong Parent Composition
Wrong Rest Pose
Wrong Bind Relationship
Wrong Skinning Matrix
Incorrect Writeback
Duplicate Evaluation
Constraint Conflict
```

First isolate the failing layer.

---

## 21. Do Not Modify Rest Pose to Hide Runtime Errors

Forbidden pattern:

```text
Runtime Pose Wrong
      ↓
Change Bone.matrix_local
      ↓
Runtime Pose Looks Correct
```

This may hide the actual conversion bug while corrupting the
underlying armature semantics.

If a runtime pose is wrong, first inspect:

```text
PoseBone
matrix_basis
parent transform
conversion
offset
constraints
```

---

## 22. Animation Keyframe Rule

When modifying animation data, distinguish:

```text
FCurve
Action
PoseBone channels
Evaluated Pose
```

A change to an evaluated transform does not necessarily mean the
underlying animation data should be modified.

Before inserting or changing keyframes, determine whether the desired
result is:

```text
persistent animation data
```

or:

```text
runtime evaluated pose
```

---

## 23. Dependency Graph Awareness

Blender's final pose may depend on:

```text
Animation
Drivers
Constraints
IK
Parent hierarchy
Physics
Modifiers
```

Therefore, after changing upstream data, do not assume that a stale
matrix represents the final state.

When validation depends on evaluated state, explicitly ensure that
the relevant Blender evaluation has occurred.

Do not "fix" stale evaluation by changing transform mathematics.

---

## 24. Evaluation Order

When debugging:

```text
Input
 ↓
Animation
 ↓
Drivers
 ↓
Constraints / IK
 ↓
Physics
 ↓
Pose Evaluation
 ↓
Deformation
```

verify the actual project-specific order.

Do not assume the order solely from this conceptual diagram.

---

## 25. Transform Writeback Rule

When writing a known pose-space matrix into Blender, prefer an
explicit Local/Pose conversion rather than pretending that the
pose-space matrix is local.

Conceptually:

```text
Known Pose Matrix
        ↓
Pose → Local conversion
        ↓
matrix_basis
        ↓
Blender Evaluation
```

Blender's API documentation provides a corresponding
Local/Pose conversion mechanism.

---

## 26. Recursive Hierarchy Updates

If multiple bones are updated manually, parent changes may affect
child pose calculations.

Therefore:

```text
Parent
  ↓
Child
    ↓
Grandchild
```

should be processed with explicit hierarchy awareness.

Do not assume that assigning every `PoseBone.matrix` independently
produces a consistent hierarchy.

For bulk pose updates, inspect Blender's documented approach using
parent-aware local/pose conversion.

---

## 27. Blender-Specific Forbidden Assumptions

The Agent MUST NOT assume:

```text
PoseBone.matrix == matrix_basis

PoseBone.matrix == Bone.matrix_local

Bone.matrix_local == world matrix

RigidBody matrix == PoseBone.matrix

Global rotation == local rotation

Changing Bone == changing animation pose

Changing PoseBone == changing rest structure

Correct screenshot == correct transform

Correct one frame == correct animation
```

---

## 28. Blender Validation Delta

通用 debug record、Golden Pose、Regression、Numerical / Temporal / Visual validation、error localization 与 change checklist 由 [`transform-space-expert-trait.md`](./transform-space-expert-trait.md) 定义；本 trait 只增加 Blender-specific requirements：

- Debug evidence MUST label Bone、PoseBone、Object、Armature、rest / pose / evaluated state and the exact space。
- Golden Pose / regression SHOULD cover parent hierarchy、rest pose、`matrix_basis` / `matrix` conversion、constraints / IK、depsgraph evaluation and physics writeback when applicable。
- Final QA MUST observe the evaluated Armature after dependency-graph updates; raw channel values or a pre-constraint pose are insufficient。
- A mesh symptom MUST first be classified as transform、constraint / IK、physics writeback、skinning or presentation; do not edit rest pose to hide runtime errors。
- Completion requires Blender-native space conversion where available and evidence that no conversion or hierarchy update is duplicated。

---

## 29. Highest-Priority Rule

> **In Blender, never treat a matrix as "just a matrix".**

Every matrix MUST be interpreted according to:

```text
Blender Object
+
Animation Stage
+
Coordinate Space
+
Parent Relationship
+
Rest Pose
+
Evaluation State
```

Before changing:

```text
A @ B
```

the Agent must understand what `A` and `B` mean.

---

## 31. Final Principle

When modifying Blender animation code, ask in this order:

```text
1. What Blender object am I modifying?

2. What animation stage does it represent?

3. What coordinate space is the transform in?

4. What is the parent/rest relationship?

5. What conversion already exists?

6. What semantic offset already exists?

7. What does Blender expect at this API boundary?

8. Only then:
   How should the matrices be composed?
```

The Agent MUST NOT reverse this order.

The correct question is not:

> "How can I make this matrix produce the desired pose?"

It is:

> "What Blender transform does this value semantically represent,
> and what is the correct conversion path to that representation?"

---

## 非目标

- 不替代具体 Graph 的 Gate / 证据包契约（见 [`pipelines-trait.md`](./pipelines-trait.md)）
- 不替代通用 transform 语义（见 [`transform-space-expert-trait.md`](./transform-space-expert-trait.md)）；本 trait 专责 Blender 层边界
- 不把本 trait 默认同化进子仓 `traits/`
