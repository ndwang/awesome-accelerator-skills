# Bmad Lattice Syntax -- Advanced Reference

## Table of Contents

1. [Statement Ordering Rules](#statement-ordering-rules)
2. [Superposition](#superposition)
3. [Multipass](#multipass)
4. [Advanced Line Features](#advanced-line-features)
5. [Expand Lattice and Post-Expansion Operations](#expand-lattice-and-post-expansion-operations)
6. [Nonstandard Parameter Syntax](#nonstandard-parameter-syntax)
7. [Custom Element Attributes](#custom-element-attributes)
8. [Beam Initialization](#beam-initialization)
9. [Parameter Structures](#parameter-structures)
10. [Lattice Conversion](#lattice-conversion)
11. [Utility Statements](#utility-statements)
12. [Digested Files](#digested-files)

---

## Statement Ordering Rules

Statements in a lattice file can generally appear in any order. Lines referenced in `use` can
come after the `use` statement, and controller elements (`group`, `overlay`) can be defined
before their slaves.

Exceptions:

- If an `expand_lattice` statement is present, all `line`, `list`, and `use` statements
  needed for expansion must come before it.
- Arithmetic expressions use immediate evaluation, so variables must be defined before use.
- An element must be defined before any of its parameters are set:

```
pp[z_offset] = 0.1    ! ERROR: pp not yet defined
pp: patch
```

- Wildcard attribute assignments only affect elements already defined:

```
crystal::*[b_param] = 0.2
c5: crystal              ! c5 is NOT affected by the line above
```

---

## Superposition

Superposition handles spatially overlapping elements (e.g., a quadrupole inside a solenoid).
Bmad creates `super_lord` elements (the physical elements) and `super_slave` elements
(the beam-path segments).

### Basic Syntax

```
Q: quad, l = 4
D: drift, l = 12
S: solenoid, l = 8, superimpose, ref = Q, ele_origin = beginning
M: marker, superimpose, ref = S, offset = 1
lat: line = (Q, D)
use, lat
```

Alternative forms:

```
Q: quad, superimpose, ...            ! Attribute on element definition
Q: quad, superimpose = T, ...        ! Explicit logical
Q[superimpose] = T                   ! Set after definition
superimpose, element = Q1, ref = B12, offset = 1.3  ! Standalone statement
```

### Placement Parameters

```
ref          = <element>       ! Reference element (default: start of branch 0)
offset       = <length>        ! Longitudinal offset (default: 0)
ele_origin   = beginning | center | end   ! Origin on superimposed element
ref_origin   = beginning | center | end   ! Origin on reference element
wrap_superimpose   = <Logical>            ! Wrap around lattice ends? (default: True)
create_jumbo_slave = <Logical>            ! Create jumbo super_slaves? (default: False)
```

Wildcards are allowed in `ref`. If `ref` matches multiple elements, one superposition
is made per match. Example splitting all quads:

```
M: null_ele, superimpose, ref = quadrupole::*
```

### Superposition and Drifts

When superposition overlaps a drift, the drift vanishes (no lord created). Drifts may not
be superimposed, and drifts may not be referenced by instance number (`ref = a_drft##2`
is an error). Use `pipe` if aperture limits on drifts must survive superposition.

### Jumbo Super_Slaves

Standard superposition splits elements at overlap boundaries. This can mishandle edge
effects for misaligned elements with nonzero fields. Jumbo super_slaves create one large
slave spanning all overlapping elements:

```
S: solenoid, l = 8, superimpose, ref = Q, ele_origin = beginning,
             create_jumbo_slave = T
```

Jumbo slaves require `runge_kutta` or `time_runge_kutta` tracking and `mat6_calc_method = tracking`.

Lord padding attributes on super_lords:

```
lord_pad1    ! Distance from upstream edge of jumbo slave to lord
lord_pad2    ! Distance from downstream edge of lord to downstream edge of jumbo slave
```

Invariant: `sum(slave lengths) = lord length + lord_pad1 + lord_pad2`.

### Superposition Wrapping

By default, a superimposed element extending past the lattice ends wraps around (even for
open geometry). Set `wrap_superimpose = F` to disable wrapping; the element is truncated.

### Superposition and Element Reversal

When the reference element is reversed, the superimposed element is also reversed and the
sense of `offset`, `ref_origin`, and `ele_origin` are mirrored so relative placement
remains consistent.

### Changing Lengths with Superposition

After parsing, varying the length of a super_lord (via `group` or `overlay`) changes only
the most downstream super_slave's length. To control which slave changes, reference
individual slaves or use `var = {end_edge}`.

### No_Superimpose Statement

`no_superimpose` turns off all superpositions. If placed after `expand_lattice`, it only
blocks superpositions defined after it.

---

## Multipass

Multipass handles beams traversing the same physical element multiple times (e.g., an ERL
linac) or elements shared between branches (e.g., an interaction region in colliding beams).

### Syntax

```
RF1: lcavity, ...
linac: line[multipass] = (RF1, ...)
erl: line = (linac, ..., linac)
use, erl
expand_lattice
RF1\2[phi0_multipass] = 0.5
```

The tracking lattice contains `RF1\1, ..., RF1\2, ...` (multipass slaves) with a
`multipass_lord` element `RF1` in the lord section. Changes to the lord propagate to all
slaves automatically.

### Grouping Rules

Elements with the same position index within the same `line[multipass]` are slaved
together. Multiple elements of the same name within a multipass line are treated as
physically distinct. If only one pass exists (the multipass line appears once), no lord is
created.

### Non-Intrinsic Attributes

These attributes can differ between slaves without affecting the lord:

```
csr_ds_step           num_steps
csr_method            ptc_integration_type
ds_step               spin_tracking_method
field_calc            space_charge_method
integrator_order      tracking_method
mat6_calc_method      phi0_multipass
```

### Reference Energy

If `e_tot` or `p0c` is set for the multipass lord in the lattice file, that value is used.
Otherwise the lord inherits the reference energy of the first-pass slave. For bends, `dg`
is adjusted per slave so the unnormalized field is the same for all slaves. All slaves have
`field_master` set to True.

### phi0_multipass

`phi0_multipass` offsets the RF phase for individual multipass slaves. With relative time
tracking, it controls both the reference energy change and the RF phase seen by a tracked
particle. With absolute time tracking, `phi0_multipass` only affects the reference energy;
to get deceleration, adjust the transit time to be an odd multiple of half the RF period.

```
expand_lattice
LC\2[phi0_multipass] = 0.5   ! Makes second pass decelerate
```

---

## Advanced Line Features

### Line Reflection and Repetition

```
line2: line = (d, -line1, e)        ! Reflect: reverse element order
line2: line = (d, 2*line1, e)       ! Repeat line1 twice
line2: line = (d, -2*(a, b, c), e)  ! Reflect and repeat inline subline
```

Reflection reverses element order but does NOT reverse individual elements (e.g., bend
face angles `e1`/`e2` are not swapped).

### Element Orientation Reversal

Double-negative `--` reverses individual elements (particles enter at exit end):

```
line2: line = (--line1)   ! Reflect AND reverse each element
```

Reversed elements have `orientation = -1`. A reflection `patch` is required between
reversed and unreversed elements. Reversal is mainly for multipass colliding-beam scenarios.

### Line Slices

Extract a sub-range of elements from a line:

```
line1: line = (a, b, c, d, e)
line2: line = (z1, line1[b:d], z2)   ! Expands to: z1, b, c, d, z2
```

Omit start or end to go to the boundary: `line4[:q1]` means from the start through `q1`.
Use `##` for nth instance: `line1[q1##2:q1##3]`.

### Replacement Lists

A `list` cycles through its members for each occurrence in a line:

```
my_list: list = (a, b, c)
line1: line = (z1, my_list, z2, my_list, z3, my_list)
! Expands to: z1, a, z2, b, z3, c
```

List members can only be simple elements (not lines). Wraps around if exhausted.

### Lines with Replaceable Arguments

```
cell(Q, B): line = (Q, drift1, B, drift2)
ring: line = (cell(qf, bend1), cell(qd, bend2))
```

Arguments can only be elements or lines (not expressions like `2*y`).

### Tagging

Tags create unique names for repeated line instances:

```
line1: line = (a, b)
line2: line = (t1@line1, t2@line1)
! Elements: t1.a, t1.b, t2.a, t2.b
```

Nested tags concatenate: `z1.t1.a`. Tagged elements can only be modified after
`expand_lattice`.

### Fork and Photon_Fork

`fork` and `photon_fork` elements connect branches. The number of branches equals
the number of lines in the `use` statement plus the number of fork/photon_fork elements
branching to new lines.

---

## Expand Lattice and Post-Expansion Operations

```
expand_lattice
```

Normally expansion happens automatically at the end of parsing. An explicit
`expand_lattice` forces immediate expansion. Only one expansion occurs; subsequent
statements are ignored.

### Expansion Steps

1. Instantiate lines from the `use` statement (including fork targets)
   - Expand sub-lines into element sequences
   - Apply superpositions
2. Form multipass lords/slaves
3. Add girder control elements
4. Add group and overlay control elements

### Operations Requiring Post-Expansion

- Setting `phi0_multipass` (multipass slaves don't exist until expansion)
- Setting attributes of tagged elements (e.g., `t1.b[k1] = 1.37`)
- Using `ran()` / `ran_gauss()` with elements appearing multiple times

### Post-Expansion Statements

These statements are valid only after expansion:

- `calc_reference_orbit` -- computes closed orbit or orbit from `particle_start`
- `merge_elements` -- merges consecutive compatible elements
- `combine_consecutive_elements` -- combines elements of same name
- `remove_elements` -- removes matching elements from the lattice
- `slice_lattice` -- splits elements at specified positions
- `start_branch_at` -- redefines the starting element of a branch

---

## Nonstandard Parameter Syntax

Some parameters use structured syntax beyond `ename[param] = value`:

**Cartesian map terms:**
```
ename[cartesian_map(N)%field_scale]
ename[cartesian_map(N)%t(M)%kx]       ! M-th term in N-th map
```

**Taylor map terms:**
```
ename[tt<out><n1><n2>...]       ! Orbital terms, e.g. tt13 -> M13
ename[ttSx<n1><n2><n3>...]     ! Spin quaternion terms
```

**Wall definitions:**
```
ename[wall%section(N)%s]
ename[wall%section(N)%v(M)%x]
ename[wall%section(N)%v(M)%radius_x]
```

**Controller knot points:**
```
ename[x_knot(N)]
ename[slave(M)%y_knot(N)]
```

**Custom attribute vectors:**
```
ename[r_custom(N1, N2, N3)]    ! 3D vector, negative indices OK
ename[r_custom(N1)]            ! Equivalent to r_custom(N1, 0, 0)
```

**Cylindrical map, gen_grad_map, grid_field, long-range wake, AC_kicker, surface
curvature** all follow similar `ename[struct(N)%component]` patterns.

---

## Custom Element Attributes

Up to 40 named custom attributes can be defined per element class:

```
parameter[custom_attribute1] = quadrupole::error_k1   ! Class-specific
parameter[custom_attribute1] = mag_id                  ! Common (all other classes)
parameter[custom_attribute2] = parameter::cost         ! Global lattice parameter
```

Class-specific definitions take precedence over common ones. Once defined, a custom
attribute can be set:

```
parameter[cost] = 140000000
l2a: lcavity, rms_phase_err = 0.0034
```

The definition must precede usage. Custom attributes are global across all lattices in a
program. Super_slave elements do NOT inherit custom attributes from their super_lords.

The `r_custom` 3D vector is always available on every element without prior definition:

```
qq: quadrupole, r_custom(-2,1,5) = 34.5
```

---

## Beam Initialization

### beam_init_struct

Key fields for generating beam distributions:

| Field | Description |
|-------|-------------|
| `position_file` | File name for file-based init (triggers file read if non-blank) |
| `distribution_type(3)` | Per-plane: `""` / `"RAN_GAUSS"`, `"ELLIPSE"`, `"KV"`, `"GRID"` |
| `n_particle` | Number of particles (for RAN_GAUSS) |
| `n_bunch` | Number of bunches |
| `a_norm_emit`, `b_norm_emit` | Normalized emittances |
| `a_emit`, `b_emit` | Unnormalized emittances |
| `sig_z`, `sig_pz` | Longitudinal sigmas |
| `dpz_dz` | pz-z correlation |
| `center(6)` | Phase space center offset |
| `bunch_charge` | Charge per bunch |
| `species` | Particle species (default: reference particle) |
| `use_particle_start` | If True, use `particle_start` for center/spin |
| `full_6D_coupling_calc` | Use full 6x6 matrix for coupled distributions |
| `random_engine` | `"pseudo"` (default) or `"quasi"` |
| `random_sigma_cutoff` | Limit max sigma generated (-1 = no cutoff) |

Total particles = product of individual distribution sizes, except `RAN_GAUSS` overlays
rather than multiplies with other types.

### File-Based Initialization

ASCII format: header lines starting with `#`, last header line starts with `#!` defining
column names, followed by particle data rows.

```
# species = proton
# charge_tot = 3.2e-9
#!  index  x       px      y       py      z       pz
    1      1.2e-3  0.5e-3  -0.3e-3 0.1e-3  2.0e-3  -1.0e-4
    ...
```

Column names map to `coord_struct` components: `x`, `px`, `y`, `py`, `z`, `pz`,
`spin_x`, `spin_y`, `spin_z`, `state`, `charge`, etc. HDF5 binary format is also
supported.

---

## Parameter Structures

### bmad_com (bmad_common_struct)

Global parameters set in lattice files with `bmad_com[param] = value`. Key fields:

**Tracking tolerances:**
- `abs_tol_tracking` (default 1e-11) -- closed orbit absolute tolerance
- `rel_tol_tracking` (default 1e-8) -- closed orbit relative tolerance
- `abs_tol_adaptive_tracking` (default 1e-10) -- Runge-Kutta absolute tolerance
- `rel_tol_adaptive_tracking` (default 1e-8) -- Runge-Kutta relative tolerance

**Step sizes:**
- `default_ds_step` (default 0.2) -- integration step size
- `init_ds_adaptive_tracking` (default 1e-3) -- initial adaptive step
- `max_num_runge_kutta_step` (default 10000) -- max RK steps before particle lost

**Physics toggles (all default False unless noted):**
- `absolute_time_tracking` -- absolute vs relative RF time
- `radiation_damping_on` -- radiation damping in tracking
- `radiation_fluctuations_on` -- radiation fluctuations
- `spin_tracking_on` -- spin tracking
- `csr_and_space_charge_on` -- CSR and space charge
- `sr_wakes_on` (default True) -- short-range wakes
- `lr_wakes_on` (default True) -- long-range wakes
- `aperture_limit_on` (default True) -- enforce aperture limits

**Other:**
- `max_aperture_limit` (default 1e3) -- maximum allowed amplitude
- `significant_length` (default 1e-10) -- length comparison threshold
- `taylor_order` (default 3) -- Taylor map order
- `d_orb(6)` (default 1e-5) -- orbit displacement for tracking-based matrices

Settings in a lattice file are "sticky" -- they persist across lattice file reads and
affect all computations.

### ptc_com (ptc_common_struct)

```
ptc_com[exact_model]    = True    ! PTC exact model
ptc_com[exact_misalign] = True    ! PTC exact misalignment
ptc_com[max_fringe_order] = 2     ! Max fringe order (2 = quadrupole)
```

---

## Lattice Conversion

Conversion tools are in the Bmad Distribution's `util_programs/` directory.

| Conversion | Tool |
|------------|------|
| MAD8/MADX to Bmad | `util_programs/mad_to_bmad/` (Python) |
| Bmad to MAD8/MADX | Tao or `util_programs/bmad_to_mad_sad_elegant` |
| SAD to Bmad | `util_programs/sad_to_bmad/sad_to_bmad.py` |
| Bmad to SAD | Tao or `util_programs/bmad_to_mad_sad_elegant` |
| Elegant to Bmad | `util_programs/elegant_to_bmad/elegant_to_bmad.py` |
| Bmad to Elegant | Tao or `util_programs/bmad_to_mad_sad_elegant` |
| Bmad to PTC flatfile | Tao: `ptc init` then `write ptc` |

Key differences when converting from MAD: Bmad has no action commands, requires variables
defined before use, and does not allow variable redefinition. Bmad elements like `wiggler`
and `sol_quad` have no MAD equivalent; the converter substitutes drift-matrix-drift or
bend-drift models.

---

## Utility Statements

### setenv

Set environment variables for use in `call` file paths:

```
setenv SUB_DIR = sub/version2
call, file = $SUB_DIR/lat2.bmad
```

`LATTICE_ROOT_DIR` is automatically set to the top-level lattice file's directory.
Environment variables are local to the program session.

### print

Print messages during parsing. Use back-ticks to interpolate values:

```
print Q01 strength: `q01[k1]` not yet optimized!
print 2 + 2 = `2+2`
```

### title

Set a title string:

```
title, "CESR Phase III Lattice"
```

Or as two lines:

```
title
"CESR Phase III Lattice"
```

### return / end_file

Stop reading the current file. Everything after is ignored.

### redef

Variables in Bmad cannot normally be redefined (unlike MAD). If a variable `x = 1` is set,
`x = 2` later would be an error. Element attributes, however, can be modified after
definition using `ename[attr] = new_value`.

---

## Digested Files

After parsing, Bmad creates a binary "digested file" containing the fully constructed
lattice including transfer maps. On subsequent runs with the same lattice, the digested
file is loaded instead of re-parsing, which can save significant time (especially with
Taylor-map wigglers).

Key behaviors:

- Created in the same directory as the lattice file
- Automatically invalidated if any source lattice file has been modified
- Skipped if random number functions (`ran`, `ran_gauss`) were used during construction
- Can be used to transport adjusted lattices between programs
- If the directory is not writable, a warning is issued but the program runs normally
- Transfer matrix generation during parsing can be controlled with
  `parameter[parser_make_xfer_mats]` (default True)
