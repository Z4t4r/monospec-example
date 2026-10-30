# ue5-animation-domain-expert

# Trait: UE5 Animation Domain Expert

> Scope: Unreal Engine 5 skeletal animation, AnimSequence,
> AnimInstance, AnimGraph, Skeletal Control, Bone Transform,
> Component Space, Local Space, Physics, IK, Control Rig,
> Animation Evaluation, and Physics Writeback.
>
> Purpose: Prevent AI Agents from applying generic transform,
> matrix, or animation logic incorrectly inside UE5.

加载时机：触及下文 Activation 所列任一任务，或改动会影响最终 evaluated skeletal pose 时，**MUST** 先读完全文再动手。  
本 trait **只**留在 monospec `traits/`。**MUST NOT** 同步到 `repos/*/traits/` 或子仓业务树。

与 [`transform-space-expert-trait.md`](./transform-space-expert-trait.md) 同时生效时：通用 transform 语义由该 trait 约束；本 trait 约束 UE5 动画层（Local / Component / CompactPose / AnimGraph / Physics writeback）的边界。冲突时，以更严格者为准。  
与 [`blender-animation-domain-expert-trait.md`](./blender-animation-domain-expert-trait.md) 同时生效时：各管自域；跨 Blender ↔ UE 转换时两者 **MUST** 同时加载，并叠加 transform-space-expert。

---

## 1. Activation

This Trait MUST be applied whenever a task involves:

- USkeletalMesh
- USkeleton
- UAnimSequence
- UAnimInstance
- UAnimMontage
- AnimGraph
- AnimNode
- FCompactPose
- FComponentSpacePoseContext
- FTransform
- FBoneTransform
- FReferenceSkeleton
- FCompactPoseBoneIndex
- FSkeletonPoseBoneIndex
- BoneContainer
- Skeletal Control
- Transform Bone
- Copy Bone
- Modify Bone
- IK
- Control Rig
- Physics Asset
- Chaos physics
- Physics-to-bone writeback
- animation evaluation
- bone local/component/world conversion
- custom animation DLL integration
- custom skeletal solver
- custom physics solver

If a change can affect the final evaluated skeletal pose,
assume this Trait applies.

---

## 2. Core Principle

## UE5 animation transforms are semantic values, not generic matrices.

Never assume:

```text
FTransform == World Transform
```

Never assume:

```text
Bone Transform == Component Transform
```

Never assume:

```text
Animation Sequence Transform == Final Evaluated Transform
```

Never assume:

```text
Physics Transform == Bone Transform
```

The Agent MUST identify the transform's semantic layer before
changing its mathematics.

---

## 3. UE5 Transform Layers

Treat the following as different layers:

```text
Reference Pose
    ↓
Animation Pose
    ↓
Local Bone Pose
    ↓
Compact Pose
    ↓
Component Space Pose
    ↓
Skeletal Control / IK
    ↓
Physics
    ↓
Final Evaluated Pose
    ↓
Skeletal Mesh Component
    ↓
World Space
```

The exact evaluation path MUST be verified for the affected system.

Do not assume every animation pipeline contains every layer.

---

## 4. Local Space vs Component Space

This is a HIGH-PRIORITY rule.

Before modifying an FTransform, determine whether it is:

```text
Local Bone Space
```

or:

```text
Component Space
```

These are NOT interchangeable.

Conceptually:

```text
Parent Component Transform
        +
Child Local Transform
        ↓
Child Component Transform
```

The exact UE5 implementation and multiplication convention MUST be
verified from the relevant API and existing code.

---

## 5. Never Apply Component Transform as Local Transform

Forbidden pattern:

```text
BoneLocal = SomeComponentTransform
```

unless the code explicitly proves that the source and target spaces
are identical.

Likewise:

```text
ComponentTransform = BoneLocal
```

is invalid unless the required parent hierarchy has been accounted for.

---

## 6. FTransform Is Not a Matrix Placeholder

Do not treat:

```text
FTransform
```

as merely:

```text
Matrix
```

FTransform has semantic components:

```text
Translation
Rotation
Scale
```

When converting to or from matrices, determine:

```text
source space
target space
multiplication convention
parent relationship
scale behavior
```

Do not introduce matrix conversions merely because they appear
convenient.

Prefer UE5-native FTransform operations where they preserve the
required semantics.

---

## 7. FTransform Composition

Before using:

```text
A * B
```

the Agent MUST determine:

```text
What space does A represent?
What space does B represent?
What is the resulting space?
Is either transform parent-relative?
Is either transform a coordinate-basis conversion?
```

Do NOT assume:

```text
A * B == B * A
```

Composition order MUST be justified semantically.

---

## 8. Bone Transform Semantics

A UE5 skeletal bone normally participates in a hierarchy.

Therefore:

```text
Child Transform
```

cannot be understood independently of:

```text
Parent Transform
Reference Pose
Bone Hierarchy
```

When modifying a bone, identify whether the operation is:

```text
Local Bone Transform
Component Space Transform
World Space Transform
```

or:

```text
Reference / Retargeting Transform
```

Do not silently switch between them.

---

## 9. Reference Skeleton

Reference pose data MUST be treated as structural input.

Inspect:

```text
FReferenceSkeleton
RefBonePose
BoneInfo
Parent Index
```

before changing skeleton-level transforms.

Do NOT modify reference-pose data to hide an animation evaluation bug.

Runtime animation problems SHOULD normally be fixed in:

```text
Animation
AnimGraph
Skeletal Control
Solver
Physics
Transform Conversion
```

rather than by corrupting reference-pose semantics.

---

## 10. Animation Sequence vs Final Pose

An AnimSequence is NOT necessarily the final pose seen by the mesh.

Potential pipeline:

```text
AnimSequence
    ↓
AnimInstance
    ↓
AnimGraph
    ↓
Skeletal Controls
    ↓
IK
    ↓
Physics
    ↓
Final Pose
```

Therefore:

```text
AnimSequence keyframe
```

MUST NOT be treated as proof of:

```text
Final evaluated bone transform
```

when downstream evaluation exists.

---

## 11. Final Evaluated Pose Is the QA Target

For animation correctness, distinguish:

```text
Stored Animation Data
```

from:

```text
Evaluated Pose
```

When the goal is to verify the result of a solver, the primary validation target SHOULD be the
final evaluated pose at the intended evaluation boundary.

Do not validate only the source AnimSequence if downstream solver
or physics stages can modify the pose.

---

## 12. Compact Pose

When working inside UE5 animation evaluation, distinguish:

```text
Skeleton Bone Index
Compact Pose Bone Index
```

These indexes MUST NOT be treated as interchangeable.

Before accessing or modifying pose data:

```text
verify the index domain
verify the BoneContainer
verify required mappings
```

Never assume:

```text
CompactPoseBoneIndex == SkeletonBoneIndex
```

---

## 13. BoneContainer

When using compact pose data, verify:

```text
BoneContainer
```

before interpreting a bone index.

The Agent MUST NOT assume that:

```text
array index N
```

means the same bone across:

```text
Skeleton
Reference Skeleton
Compact Pose
Required Bones
```

---

## 14. FBoneTransform

When using:

```text
FBoneTransform
```

identify:

```text
Bone Index
Transform Space
Transform Meaning
```

Do not assume that an FBoneTransform automatically represents a
world-space transform.

When a Skeletal Control modifies FBoneTransform values, determine
whether the node expects:

```text
Local Space
```

or:

```text
Component Space
```

or another node-specific space.

---

## 15. Skeletal Control

Before modifying a Skeletal Control, inspect its declared or actual
evaluation space.

Typical pattern:

```text
Local Space
    ↓
Convert to Component Space
    ↓
Perform Control
    ↓
Convert back
    ↓
Local Pose
```

Do not add an additional conversion if the framework already
performs it.

---

## 16. Component Space Conversion

High-risk operations include:

```text
Local → Component
Component → Local
```

Before implementing either conversion, verify:

```text
Parent Bone
Reference Pose
Current Parent Pose
Bone Hierarchy
Existing UE5 conversion utilities
```

Prefer established UE5 animation APIs and project utilities over
reimplementing hierarchy mathematics.

---

## 17. Parent Hierarchy

When multiple bones are modified:

```text
Parent
   ↓
Child
   ↓
Grandchild
```

the evaluation order matters.

Do not calculate all children from stale parent transforms.

For a hierarchy-sensitive operation:

```text
update / evaluate parent
    ↓
obtain correct parent state
    ↓
evaluate child
```

unless the specific UE5 evaluation system defines another mechanism.

---

## 18. World Space Is a Separate Layer

Do not use:

```text
World Transform
```

when the API expects:

```text
Component Transform
```

The SkeletalMeshComponent itself may have:

```text
Actor Transform
Component Transform
World Transform
```

Therefore a bone's world transform depends on both:

```text
Skeletal Pose
```

and:

```text
Component / Actor Transform
```

Do not mix these layers.

---

## 19. Skeletal Mesh Component

A bone transform relative to the SkeletalMeshComponent is NOT
automatically a world transform.

Conceptually:

```text
Bone Component Transform
        ↓
SkeletalMeshComponent Transform
        ↓
World Transform
```

The exact API used MUST be checked before converting between them.

---

## 20. Physics Transform

Never assume:

```text
Physics Body Transform == UE Bone Transform
```

Physics may operate on:

```text
Physics Asset Bodies
Constraints
Body Instances
Component Space
World Space
```

A physics body's transform may also represent a body center or
physics-specific frame rather than the bone's semantic frame.

---

## 21. Physics-to-Bone Writeback

Physics writeback MUST be treated as a dedicated conversion stage.

Preferred conceptual model:

```text
Animation Pose
      │
      ├───────────────┐
      │               │
      ▼               ▼
Bone Evaluation    Physics Solver
      │               │
      │               ▼
      │         Physics State
      │               │
      │               ▼
      │       Physics → Bone
      │         Conversion
      │               │
      └───────┬───────┘
              ▼
         Final Pose
```

Do NOT directly assign a physics transform to a bone without proving
that both transforms have the same semantic frame.

---

## 22. Physics Body Frame vs Bone Frame

Before physics writeback, identify:

```text
Physics Body Origin
Physics Body Rotation
Bone Origin
Bone Rotation
Reference Pose Relationship
Body-to-Bone Offset
```

Potential relationship:

```text
PhysicsBody
    ↓
Body Coordinate Conversion
    ↓
Body-to-Bone Offset
    ↓
Bone Component Transform
    ↓
Bone Local Transform
```

The exact project implementation MUST be verified.

---

## 23. Physics Writeback Debugging

When physics writeback produces an incorrect pose, capture:

```text
A = Physics Solver Output
B = Converted Physics Transform
C = Bone Transform Before Writeback
D = Bone Transform After Writeback
E = Final Evaluated Pose
F = Mesh Result
```

Locate the first divergence.

If:

```text
A correct
B incorrect
```

suspect:

```text
Transform Conversion
```

If:

```text
B correct
D incorrect
```

suspect:

```text
Writeback / Bone Space
```

If:

```text
D correct
E incorrect
```

suspect:

```text
Animation Evaluation / Skeletal Control / Physics ordering
```

If:

```text
E correct
F incorrect
```

suspect:

```text
Skinning / Mesh / Reference Pose
```

---

## 24. Do Not Diagnose Solver Failure from Mesh Appearance

A visually incorrect mesh does NOT prove:

```text
Physics Solver Failure
```

Possible causes:

```text
Physics → Bone Conversion
Local / Component Space Error
Parent Composition Error
Reference Pose Error
Writeback Error
Evaluation Order
Skinning Error
```

Always locate the failing layer first.

---

## 25. Animation Evaluation Order

When modifying an animation pipeline, identify:

```text
Input Animation
    ↓
AnimGraph
    ↓
Skeletal Controls
    ↓
IK
    ↓
Physics
    ↓
Final Pose
```

The actual project may differ.

The Agent MUST inspect the actual evaluation chain rather than
assuming this conceptual order is universal.

---

## 26. Avoid Double Evaluation

High-risk pattern:

```text
Solver
   ↓
Final Pose
   ↓
Write Back
   ↓
Solver evaluates again
   ↓
Double Transform
```

Before adding a writeback path, determine whether the data is:

```text
Input
```

or:

```text
Evaluated Output
```

Do not feed an evaluated result back into an upstream stage unless
explicitly intended.

---

## 27. AnimGraph Boundary

When changing AnimGraph-related code, identify whether the transform
is:

```text
input to the node
```

or:

```text
output from the node
```

Do not modify both sides of a conversion independently.

Potential failure:

```text
Local
  ↓
Component
  ↓
Node
  ↓
Local
  ↓
Extra Component Conversion
  ↓
Incorrect Pose
```

---

## 28. IK

IK is particularly sensitive to transform space.

Before changing IK-related code, identify:

```text
Effector Space
Joint Space
Bone Space
Component Space
Pole Vector Space
Target Space
```

Do not assume all IK inputs are in Component Space.

Do not assume the output can be directly written into Local Space.

---

## 29. Control Rig

When Control Rig is involved, treat its transform semantics as
another domain boundary.

Do not assume:

```text
Control Rig Transform
```

is directly equivalent to:

```text
AnimGraph Bone Transform
```

Explicitly identify:

```text
Rig Space
Global / Local Transform
Bone Transform
Hierarchy Transform
Evaluation Stage
```

before converting.

---

## 30. Retargeting

Retargeting transforms MUST NOT be confused with ordinary animation
transforms.

Distinguish:

```text
Source Skeleton
Target Skeleton
Reference Pose
Retarget Pose
Animation Pose
Final Pose
```

Do not "fix" a retargeting issue by changing general bone-space
conversion without verifying the retargeting layer.

---

## 31. Coordinate-System Conversion

For external animation integrations, coordinate conversion MUST have
one clearly defined semantic boundary.

Example:

```text
Source Transform
      ↓
Source → UE Coordinate Conversion
      ↓
UE Bone Transform
      ↓
UE Animation Evaluation
```

Do not silently apply the same conversion again inside:

```text
AnimGraph
Skeletal Control
Physics Writeback
Rendering
```

---

## 32. XZY / Euler Conversion

Rotation order MUST be treated as semantic information.

Never assume:

```text
XZY
```

can be applied directly to:

```text
Final Bone Transform
```

without determining the transform's current space.

High-risk pattern:

```text
BoneTransform
    ↓
Global XZY
    ↓
Final Bone
```

This MUST trigger investigation.

Verify:

```text
Source Space
Target Space
Rotation Basis
Rotation Order
Parent Space
Offset
Existing Conversion
```

---

## 33. Coordinate Conversion Must Not Be Duplicated

Before adding:

```text
axis swap
basis rotation
Euler reorder
quaternion conversion
XZY
XYZ
```

search the pipeline for existing conversions.

Typical failure:

```text
Source → UE conversion
      ↓
Animation conversion
      ↓
Physics conversion
      ↓
XZY again
```

The Agent MUST determine whether the conversion has already been
performed upstream.

---

## 34. FTransform and Quaternion Order

When composing rotations:

```text
Q1 * Q2
```

the Agent MUST identify the semantic meaning of each quaternion.

Do not assume that the mathematically valid multiplication order is
the project-correct order.

Verify:

```text
Source Rotation Space
Target Rotation Space
Parent Rotation
Coordinate Basis
Rotation Convention
```

---

## 35. Scale

Scale MUST NOT be silently ignored.

When converting transforms, inspect:

```text
Translation
Rotation
Scale
```

especially when using:

```text
FTransform
Matrix
Bone Transform
Component Transform
```

Do not assume:

```text
Scale == Identity
```

unless established by the project.

---

## 36. Reference Pose Preservation

Runtime solver or physics changes MUST NOT silently alter:

```text
Reference Skeleton
Ref Bone Pose
```

unless the task explicitly modifies the skeleton definition.

If a runtime result requires a changed reference pose, first determine
whether the actual problem is:

```text
Transform Conversion
Retargeting
Animation Input
Physics Offset
Writeback
```

---

## 37. Evaluation-State Validation

When validating UE5 animation, distinguish:

```text
Stored Animation
Evaluated Animation
Physics State
Final Bone Pose
```

The QA target MUST be explicitly declared.

For solver validation, prefer:

```text
Final Evaluated Bone State
```

over:

```text
Source Animation Keyframe
```

when the solver participates in evaluation.

---

## 38. UE5 Validation Delta

通用 Numerical / Temporal Validation、Sampling、Semantic Pose、AI boundary、Golden Pose、Regression、debug protocol、high-risk operation 与 forbidden shortcut 由 [`transform-space-expert-trait.md`](./transform-space-expert-trait.md) 定义；本 trait 只增加 UE5-specific requirements：

- Evidence MUST identify Local Pose、CompactPose、Component Space、World Space 与 Physics Body Frame，不能只记录无语义的 matrix。
- Golden Pose / regression SHOULD cover Reference Skeleton mapping、BoneContainer / CompactPose index resolution、AnimGraph evaluation order、Skeletal Control conversion and any physics writeback boundary。
- Validation MUST compare final evaluated skeletal pose, not only an Animation Sequence、Control Rig node or pre-evaluation buffer。
- `FTransform` composition、scale、quaternion order and Component Space conversion MUST be checked through UE5 semantics and APIs。
- AI image judgment remains supporting evidence only; exact bone mapping、space、rotation and acceptance require numerical/runtime evidence。

---

## 39. Evidence Hierarchy

Prefer evidence in this order:

```text
1. Explicit Transform Contract
2. UE5 API / evaluation semantics
3. Project-specific verified implementation
4. Deterministic numerical invariant
5. Golden Pose / Regression Test
6. Intermediate-state comparison
7. Temporal validation
8. Semantic AI inspection
9. Screenshot / Render
```

A screenshot is supporting evidence, not the transform specification.

---

## 40. Failure Classification

Classify failures before changing the solver.

Use:

```text
ANIMATION_INPUT_ERROR
REFERENCE_POSE_ERROR
COMPACT_POSE_INDEX_ERROR
LOCAL_SPACE_ERROR
COMPONENT_SPACE_ERROR
WORLD_SPACE_ERROR
PARENT_COMPOSITION_ERROR
COORDINATE_CONVERSION_ERROR
ROTATION_ORDER_ERROR
OFFSET_ERROR
SKELETAL_CONTROL_ERROR
IK_ERROR
RETARGETING_ERROR
PHYSICS_SOLVER_ERROR
PHYSICS_WRITEBACK_ERROR
EVALUATION_ORDER_ERROR
SKINNING_ERROR
TEMPORAL_ERROR
SEMANTIC_POSE_ERROR
```

---

## 41. Layered QA

UE5 animation validation SHOULD be separated into:

```text
L1 — Input Animation
L2 — Solver State
L3 — Transform Conversion
L4 — Local Bone Pose
L5 — Component Space Pose
L6 — Physics State
L7 — Final Evaluated Pose
L8 — Temporal Stability
L9 — Semantic Pose
L10 — Visual Evidence
```

A failure MUST identify the layer.

Example:

```text
L1 PASS
L2 PASS
L3 FAIL
L4 FAIL
L5 FAIL
L6 PASS
L7 REVIEW
L8 PASS
L9 REVIEW
L10 REVIEW
```

This is more useful than:

```text
Animation FAIL
```

---

## 44. Solver Boundary

At the boundary:

```text
External Solver
        ↓
      UE5
```

explicitly document:

```text
Input Coordinate System
Output Coordinate System
Bone Space
Component Space
Rotation Convention
Translation Unit
Scale Convention
Parent Relationship
Offset Convention
```

This boundary SHOULD have numerical regression tests.

---

## 45. Unit Consistency

Before comparing transforms from different systems, verify units.

At minimum:

```text
Position Unit
Rotation Unit
Time Unit
Velocity Unit
```

Do not compare:

```text
centimeters
```

against:

```text
meters
```

without conversion.

Do not compare:

```text
degrees
```

against:

```text
radians
```

without conversion.

---

## 46. Do Not Mix Solver and Presentation

The solver SHOULD produce a deterministic transform state.

Presentation / rendering SHOULD consume that state.

Avoid modifying solver mathematics merely to make:

```text
viewport
screenshot
mesh appearance
```

look correct.

If the numerical solver state is correct but the mesh is wrong,
investigate the downstream transform / skinning path.

---

## 47. Definition of Done

A UE5 animation change is complete only when:

```text
[ ] Correct UE5 animation layer identified
[ ] Local / Component / World space identified
[ ] Skeleton Bone Index vs Compact Pose Index verified
[ ] Parent hierarchy verified
[ ] Reference Pose semantics preserved
[ ] Existing conversion utilities inspected
[ ] Coordinate conversion verified
[ ] Rotation order verified
[ ] FTransform composition order verified
[ ] Skeletal Control / IK considered
[ ] Physics state separated from Bone state
[ ] Physics writeback isolated if applicable
[ ] Evaluation order considered
[ ] Final evaluated pose validated
[ ] Numerical validation performed
[ ] Golden Pose considered
[ ] Regression test added for discovered transform bugs
[ ] Temporal validation performed where relevant
[ ] Visual result checked as supporting evidence
```

---

## 48. Highest-Priority Rule

> In UE5, never treat a bone transform as "just an FTransform".

Always determine:

```text
What object?
What bone?
What index domain?
What space?
What evaluation stage?
What parent?
What reference pose?
What solver?
What coordinate convention?
```

Only then determine:

```text
How should the transform be composed?
```

---

## 49. Final Agent Rule

When modifying UE5 animation code, ask in this order:

```text
1. What UE5 animation layer am I modifying?

2. Is this Reference, Local, Compact, Component, or World Space?

3. What bone/index domain does this value use?

4. What is the parent relationship?

5. Has coordinate conversion already occurred?

6. Is there an existing UE5 conversion utility?

7. Is this Animation, Skeletal Control, IK, Physics, or Final Pose?

8. Is this input or evaluated output?

9. What numerical invariant proves correctness?

10. Only then:
    How should the transforms be composed?
```

The Agent MUST NOT reverse this order.

The correct question is not:

```text
"How do I make this FTransform produce the desired result?"
```

It is:

```text
"What UE5 transform does this value semantically represent,
and what is the correct conversion path to that representation?"
```

---

## 非目标

- 不替代具体 Graph 的 Gate / 证据包契约（见 [`pipelines-trait.md`](./pipelines-trait.md)）
- 不替代通用 transform 语义（见 [`transform-space-expert-trait.md`](./transform-space-expert-trait.md)）；本 trait 专责 UE5 动画层边界
- 不替代 Blender 动画层边界（见 [`blender-animation-domain-expert-trait.md`](./blender-animation-domain-expert-trait.md)）
- 不把本 trait 默认同化进子仓 `traits/`
