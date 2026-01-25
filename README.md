# MGTools — Quick Reference

---

## Table of contents
- [Rigging](#rigging)
- [Weighting](#weighting)
- [Animation](#animation)
- [Object](#object)
- [Mesh](#mesh)
- [Renaming](#renaming)
- [I/O (Export)](#io-export)
- [Misc](#misc)

---

## Rigging
<table>
<tr>
<td valign="top" align="left" width="240">
<img src="docs/readme_panel_rigging.png" alt="Rigging panel" style="width:235px; max-width:100%; height:auto; display:block;" />
</td>
<td valign="top">
Snapshot, selection, and constraint retarget tools for armatures.

- **Bone Snapshot Tool**: clone bones with a configurable prefix, add a root bone, and optionally add location/rotation/scale constraints to cloned bones.
- **Bone Select Tool**: helpers to select bones quickly.
- **Retarget Constraints**: retarget object-level and bone-level constraints to another target object.
</td>
</tr>
</table>

---

## Weighting
<table>
<tr>
<td valign="top" align="left" width="240">
<img src="docs/readme_panel_weighting.png" alt="Weighting panel" style="width:235px; max-width:100%; height:auto; display:block;" />
</td>
<td valign="top">
Display and edit vertex group weights, shortcuts, and utilities to manage weights.

- Show and customize weights display color on vertices (3ds max style).
- Weight tools: create missing vertex groups, normalize weights, set quick weight values (0, .1, .25, .5, .75, .9, 1), add/subtract weight offsets, copy/paste weights, average and smooth operations.
- Mirror weights options (topology-aware or naive mirror).
- Remove empty or locked vertex groups and limit influences per vertex.
- Vertex group list view with advanced filtering and sorting (average-weight based filtering).
</td>
</tr>
</table>

---

## Animation
<table>
<tr>
<td valign="top" align="left" width="240">
<img src="docs/readme_panel_animation.png" alt="Animation panel" style="width:235px; max-width:100%; height:auto; display:block;" />
</td>
<td valign="top">
Motion path automation and copying animation data (including NLA tracks).

- **Auto Update Motion Paths**: toggle automatic motion path updates.
- **Copy Animation Data**: select a Source and Target object and copy animation data (actions and NLA tracks).
</td>
</tr>
</table>

---

## Object
<table>
<tr>
<td valign="top" align="left" width="240">
<img src="docs/readme_panel_object.png" alt="Object panel" style="width:235px; max-width:100%; height:auto; display:block;" />
</td>
<td valign="top">
Convenience tools for object-level transforms, parenting, pivot handling and snapshots.

- **Pivot**: copy active pivot to selected objects.
- **Parent**: parent objects to the active or clear parent.
- **Transforms**: set world/local location and local rotation from UI props.
- **Snapshots**: create snapshots of objects over a frame range; options for prefixing and merging.
</td>
</tr>
</table>

---

## Mesh
<table>
<tr>
<td valign="top" align="left" width="240">
<img src="docs/readme_panel_mesh.png" alt="Mesh panel" style="width:235px; max-width:100%; height:auto; display:block;" />
</td>
<td valign="top">
Mesh-focused utilities, mostly vertex group management.

- **Vertex Groups**: options to keep unique target VGs, copy vertex-group flags, a name filter, and an operator to match vertex groups to the selection.
</td>
</tr>
</table>

---

## Renaming
<table>
<tr>
<td valign="top" align="left" width="240">
<img src="docs/readme_panel_rigging.png" alt="Renaming panel" style="width:235px; max-width:100%; height:auto; display:block;" />
</td>
<td valign="top">
Rename bones, vertex groups and animation curve groups using mapping files and quick tools.

- **Rename with mapping**: provide a mapping file (text file in `old:new;` format) and optionally invert the mapping direction.
- **Prefixes**: `Remove prefix` and `Add prefix` fields (applied after mapping — removal of a leading prefix is case-sensitive and removes only the first leading occurrence; adding avoids duplication).
- **Quick rename tools**: Rename Bones, Rename Vertex Groups, Rename FCurves.
- **Convenience tools**: print names and set mesh data names from object names.
</td>
</tr>
</table>

---

## I/O (Export)
<table>
<tr>
<td valign="top" align="left" width="240">
<img src="docs/readme_panel_io.png" alt="I/O Export panel" style="width:235px; max-width:100%; height:auto; display:block;" />
</td>
<td valign="top">
Export configuration and batch export operations.

- **Axis**: set forward / up axes and bone axes.
- **Scale**: export scale and scaling behavior.
- **Pivot**: configure pivot filter prefix and options to include pivot dummies and reset transforms.
- **Helper**: strip dot-number suffixes from helper objects.
- **Mesh / Clones**: options for applying modifiers, combining cloned meshes, clone filters, prefix/postfix for object names, material override and armature replacement.
- **Vertex Groups Rename (I/O)**: enable vertex group renaming during export using a mapping file, with an option to invert the mapping and inline Remove/Add prefix fields (applied during export).
- **Animation**: bake and mode options for animation export:
  - **Modes:**
    - **RANGE** — export the current scene frame range as a single animation.
    - **STRIPS** — export each NLA strip as a separate animation (optionally use relative frame ranges).
    - **MARKERS** — use timeline markers as start/end pairs to export multiple animations.
    - **OFF** — export a single frame (no animation baked).
  - **Bake options:** key all bones, use NLA strips or all actions, force start/end keying, sampling step (frames), and simplify baked curves (reduces redundant keyframes; 0 disables).
- **File name**: configure filename prefixes/postfix and collection/selection export shortcuts.
- **Collection/Selection Export**: export entire collections or active selection via provided paths and operators.
- **Hitboxes**: batch export hitbox collections with filter.
</td>
</tr>
</table>

---

## Misc
<table>
<tr>
<td valign="top" align="left" width="240">
<img src="docs/readme_panel_misc.png" alt="Misc panel" style="width:235px; max-width:100%; height:auto; display:block;" />
</td>
<td valign="top">
Assorted tools that don't fit other sections.

- **Particle Hair → Mesh**: convert particle hair to mesh with thickness, resolution, and hair-shape curve mapping.
- **Modifier Toggle**: quick UI to toggle named modifiers on the active object.
- **Custom Attributes**: snapshot vertex positions to an attribute (name + relative option).
</td>
</tr>
</table>
