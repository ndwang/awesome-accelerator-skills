---
name: bmad
description: Write, read, edit, and understand Bmad accelerator lattice files and simulations. Use this skill whenever the user mentions Bmad, Tao, accelerator lattice files, particle beam simulation, beam optics, Twiss parameters, or storage ring / linac design. Also trigger when the user works with .bmad files, asks about element types (quadrupole, sbend, rfcavity, drift, etc.), lattice syntax, tracking methods, or accelerator physics conventions. Even if the user doesn't say "Bmad" explicitly, use this skill if they are clearly working in the domain of charged particle or X-ray beam simulation.
---

# Bmad Lattice File Skill

Bmad is an open-source software library for simulating charged particles and X-rays in accelerators
and storage rings. Bmad is not a program itself but a toolkit used by programs (most notably Tao)
for beam physics calculations. It integrates with PTC/FPP for symplectic tracking and Taylor maps.

This skill covers Bmad lattice file authoring and the physics conventions needed to understand them.
For detailed element attributes, advanced syntax, or tracking physics, see the reference files in
`skills/bmad/references/`.

## Core Concepts

**Lattice hierarchy:**
- **Element**: Basic building block (drift, quadrupole, bend, cavity, etc.)
- **Branch**: Ordered sequence of elements representing a particle path
- **Lattice**: Collection of branches that may be interconnected

Every branch automatically gets a `BEGINNING` element (index 0) and an `END` marker.

**Lord-slave relationships** allow elements to control or overlap others:
- `overlay`: Controls attributes of slave elements via expressions
- `group`: Like overlay but with variable-based expressions
- `girder`: Represents a mechanical support; controls misalignments of supported elements
- **Superposition**: Overlapping elements (e.g., quad inside solenoid) create super_lord/super_slave pairs
- **Multipass**: Elements traversed multiple times (e.g., linac in an ERL) create multipass_lord/slave pairs

## Lattice File Syntax

### Basic Rules

- **Comments**: `!` to end of line
- **Case insensitive** (except file names, crystal formulas, `type`/`alias`/`descrip` strings)
- **Semicolons**: Multiple statements on one line: `a: drift, l = 1; b: drift, l = 2`
- **Continuation**: `&` at end of line, or implicit with `, ( { [ =` at end / `, ) } ] =` at start
- **Names**: Max 40 chars. First char must be letter [A-Z], then letters/digits/underscore
- **Units**: SI throughout — meters, radians, eV, Tesla, Volts, Amps, Hz. RF phase in radians/2pi.

### Element Definition

```
ele_name: element_type, attr1 = val1, attr2 = val2, ...
```

Examples:
```
d1: drift, l = 2.5
q1: quadrupole, l = 0.6, k1 = 0.234
b1: sbend, l = 2.3, angle = 0.1, e1 = 0.05, e2 = 0.05
rf: rfcavity, l = 1.0, voltage = 5e6, harmon = 400
```

**Inheritance** — an element can inherit from a previously defined element:
```
qa: quadrupole, l = 0.6, k1 = 0.3
qb: qa                      ! QB inherits QA's attributes
qa[k1] = 0.5                ! Does NOT affect QA (immediate evaluation)
```

### Attribute Access

```
elem_name[attr_name] = value
```

No space between element name and `[`. Wildcards supported:
```
q01[k1] = 0.234                    ! Single element
quadrupole::*[k1] = 0.0            ! All quadrupoles
sbend::b0%[dg] = 0.01              ! Sbends matching "b0" + one char
*[tracking_method] = runge_kutta    ! All elements
```

After `expand_lattice`, index-based and range access:
```
expand_lattice
97[x_offset] = 0.0023
5:32[x_limit] = 0.3
q1##3[k1] = 0.1                    ! 3rd element named q1
```

### Variables and Expressions

```
my_var = sqrt(10.3) * pi^3         ! Define a constant
b1: sbend, l = 2.0, g = my_var     ! Use in element definition
```

**Immediate evaluation** — all values must be defined before use. Constants cannot be redefined
(use `redef:` prefix if absolutely necessary). Operators: `+ - * / ^`.

Built-in constants: `pi`, `twopi`, `c_light`, `m_electron`, `m_proton`, `e_charge`,
`h_planck`, `degrees` (pi/180), `degrad` (180/pi), `r_e`, and more.

Intrinsic functions: `sqrt`, `log`, `exp`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`,
`abs`, `int`, `nint`, `floor`, `ceiling`, `modulo`, `ran()`, `ran_gauss()`, `factorial`,
`mass_of(species)`, `charge_of(species)`, `anomalous_moment_of(species)`, `species(name)`.

### Line Definition

```
line_name: line = (elem1, elem2, ...)
```

Features:
```
l1: line = (a, b, c)
l2: line = (l1, d, l1)             ! Nesting: expands to (a, b, c, d, a, b, c)
l3: line = (3*a, 2*l1)             ! Repetition
l4: line = (-l1)                   ! Reflection: reverses element order -> (c, b, a)
l5: line = (--l1)                  ! Reversal: reverses elements AND their orientation
```

**Lines with arguments** (parameterized sub-lines):
```
cell(qf, qd): line = (qf, d1, bend, d2, qd, d2, bend, d1)
ring: line = (cell(q1a, q2a), cell(q1b, q2b))
```

### Use Statement

```
use, line_name                     ! Single branch lattice
use, line_a, line_b                ! Multi-branch (e.g., colliding beams)
```

### Replacement Lists

```
my_list: list = (a, b, c)
my_line: line = (z1, my_list, z2, my_list)  ! Expands: z1, a, z2, b
```
Each reference to the list uses the next item sequentially.

### Tagging

```
cell: line = (q, d, b, d)
ring: line = (s1@cell, s2@cell)    ! Elements named s1.q, s1.d, etc.
```

### File Inclusion

```
call, file = "path/to/other.bmad"
call, file = $ENV_VAR/lattice.bmad           ! Environment variable expansion
```

Relative paths are relative to the calling file's directory. `$LATTICE_ROOT_DIR` is auto-set
to the directory of the top-level lattice file.

**Inline call** for element attributes from separate files:
```
c: crystal, grid_field = call::my_grid.h5
```

### Overlay and Group Controllers

**Overlay** — controls slave attributes with expressions:
```
chicane: overlay = {bnd1[dg]:-ge, bnd2[dg]:ge}, var = {ge}, ge = 2e-3
```

**Group** — similar but sets absolute values rather than proportional:
```
my_group: group = {q1[k1]:1, q2[k1]:-0.5}, var = {strength}, strength = 0.1
```

### Parameter Statements

```
parameter[geometry] = open              ! or closed (default depends on lattice)
parameter[e_tot] = 5e9                  ! Reference total energy [eV]
parameter[p0c] = 5e9                    ! Reference momentum [eV/c] (alternative to e_tot)
parameter[particle] = electron          ! Reference species
parameter[no_end_marker] = T            ! Suppress auto END element
parameter[taylor_order] = 3             ! Taylor map order (default: 3)
parameter[n_part] = 1e10                ! Bunch population
parameter[ran_seed] = 0                 ! Random seed (0 = clock)
parameter[photon_type] = incoherent     ! or coherent
```

### Beginning Statement (Initial Conditions)

For open geometry lattices, set initial Twiss parameters:
```
beginning[beta_a] = 20.0               ! Horizontal beta function [m]
beginning[alpha_a] = -0.5
beginning[beta_b] = 15.0               ! Vertical beta function [m]
beginning[alpha_b] = 0.25
beginning[eta_x] = 0.1                 ! Horizontal dispersion [m]
beginning[etap_x] = 0.0                ! d(eta_x)/ds
beginning[e_tot] = 5e9                 ! Can override parameter[e_tot]
beginning[theta_position] = 0.3        ! Initial global angle
```

### Particle Species

```
parameter[particle] = electron          ! Fundamental particles
parameter[particle] = #12C+3           ! Triply charged carbon-12
parameter[particle] = He--             ! Doubly negative helium
parameter[particle] = @M37.54++        ! Mass + charge only
```

Fundamental species: `electron`, `positron`, `proton`, `antiproton`, `muon`, `antimuon`,
`neutron`, `photon`, `pion+`, `pion-`, `pion0`, `deuteron`.

## Key Element Types

| Element | Description | Primary Attributes |
|---------|-------------|-------------------|
| `drift` | Free space | `l` |
| `quadrupole` | Focusing/defocusing | `l`, `k1` (or `b1_gradient`) |
| `sbend` | Sector dipole bend | `l`, `angle` (or `g`), `e1`, `e2`, `dg` |
| `rbend` | Rectangular bend (converts to sbend) | `l`, `angle` |
| `sextupole` | Chromaticity correction | `l`, `k2` |
| `octupole` | Higher-order correction | `l`, `k3` |
| `solenoid` | Axial field magnet | `l`, `ks` (or `bs_field`) |
| `rfcavity` | RF accelerating cavity | `l`, `voltage`, `harmon`, `phi0` |
| `lcavity` | Linac cavity | `l`, `voltage`, `phi0`, `gradient` |
| `marker` | Zero-length reference point | — |
| `monitor` / `instrument` | Beam diagnostics | `l` |
| `hkicker` / `vkicker` | Steering correctors | `l`, `kick` |
| `kicker` | General kicker | `l`, `hkick`, `vkick` |
| `multipole` | Thin multipole | `k0l`..`k21l`, `t0`..`t21` |
| `patch` | Coordinate transformation | `x_offset`, `y_offset`, `z_offset`, `x_pitch`, `y_pitch`, `tilt` |
| `floor_shift` | Global coordinate shift | `x_offset`, `y_offset`, `z_offset`, `x_pitch`, `y_pitch`, `tilt` |
| `fork` / `photon_fork` | Branch to another line | `to_line`, `to_element` |
| `overlay` | Attribute controller | `var`, slave list with expressions |
| `group` | Variable-based controller | `var`, slave list with expressions |
| `girder` | Mechanical support | element list, misalignment attrs |
| `wiggler` | Periodic field for SR | `l`, `b_max`, `n_period` |
| `ecollimator` / `rcollimator` | Aperture limiter | `l`, `x_limit`, `y_limit` |
| `e_gun` | Electron source | `l`, `voltage` |
| `sol_quad` | Solenoid + quadrupole | `l`, `ks`, `k1` |
| `crab_cavity` | Transverse RF kick | `l`, `voltage`, `harmon` |
| `crystal` | X-ray Bragg optics | `crystal_type`, `b_param`, `curvature` |
| `mirror` | Photon reflector | `graze_angle` |
| `photon_init` | Photon beam source | `sig_x`, `sig_y`, energy distribution params |
| `fiducial` | Reference alignment point | `origin_ele` |
| `match` | Optics matching | target Twiss values |
| `beambeam` | Beam-beam interaction | beam parameters |
| `taylor` | Taylor map element | `tt` coefficients |
| `em_field` | General EM field | field maps |
| `ac_kicker` | Time-dependent kicker | `amp_vs_time`, `frequencies` |

For complete attributes per element type, see `references/elements.md`.

## Tracking Methods

Each element has three method attributes:

| Attribute | Purpose | Common Values |
|-----------|---------|---------------|
| `tracking_method` | Particle tracking | `bmad_standard`, `runge_kutta`, `symp_lie_ptc`, `linear`, `taylor` |
| `mat6_calc_method` | Transfer matrix | `bmad_standard`, `tracking`, `symp_lie_ptc` |
| `spin_tracking_method` | Spin tracking | `tracking`, `sprint`, `custom` |

- **`bmad_standard`** (default for most): Fast, analytic formulas, paraxial approximation
- **`runge_kutta`**: Accurate numerical integration, handles complex fields, slower
- **`symp_lie_ptc`**: Symplectic via PTC library, good for long-term tracking
- **`linear`**: First-order only, very fast

Step-size control: `ds_step` (step size in meters) or `num_steps` (number of steps).

## Coordinates and Phase Space

**Three coordinate frames:**
1. **Global (floor)**: Fixed lab frame (x, y, z) for physical layout
2. **Local (laboratory)**: Curvilinear frame following the reference orbit; z along beam direction
3. **Element body**: Attached to the element, used for field calculations

**Phase space coordinates**: $(x, p_x, y, p_y, z, p_z)$
- $x, y$: Transverse position [m] relative to reference orbit
- $p_x = P_x / P_0$, $p_y = P_y / P_0$: Normalized transverse momenta (approximately slopes $x', y'$)
- $z = -\beta c (t - t_{\text{ref}})$: Longitudinal position relative to reference particle [m]
- $p_z = \Delta E / (P_0 c)$: Energy deviation normalized by reference momentum

## Electromagnetic Fields

**Multipole expansion** of transverse magnetic field on midplane:
- $K_n = q B_n / P_0$: Normalized strength of order $n$
- $K_0$: dipole, $K_1$: quadrupole (focusing), $K_2$: sextupole, $K_3$: octupole
- `k1` = $K_1$, `k2` = $K_2$, etc. in lattice files (normalized by default)
- `b1_gradient`, `b2_gradient`: Unnormalized field derivatives [T/m^n]
- `field_master = T`: Makes unnormalized fields the independent variables

**Skew vs. normal components**: `a0`..`a21` (skew), `b0`..`b21` (normal) for multipole errors.
Thin multipole integrated strengths: `k0l`..`k21l` with tilt angles `t0`..`t21`.

## Linear Optics

**Twiss parameters** $\alpha$, $\beta$, $\gamma$ describe the beam envelope:
- `beta_a`, `alpha_a`: Horizontal (a-mode) Twiss
- `beta_b`, `alpha_b`: Vertical (b-mode) Twiss
- `eta_x`, `eta_y`: Dispersion (position shift per unit energy deviation)

**Normal modes**: In a coupled lattice, the physical x/y planes mix. Bmad decomposes motion into
uncoupled a-mode and b-mode. The coupling matrix $\mathbf{C}$ measures the mixing strength.

## Complete Examples

### Simple Open Lattice (Linac Transfer Line)
```
parameter[geometry] = open
parameter[e_tot] = 2.7389062e9
parameter[particle] = positron
beginning[beta_a] = 14.5
beginning[alpha_a] = -0.54
beginning[beta_b] = 31.3
beginning[alpha_b] = 0.26

q: quadrupole, l = 0.6, b1_gradient = 9.011
d: drift, l = 2.5
t: line = (q, d)
use, t
```

### Storage Ring Cell
```
parameter[geometry] = closed
parameter[p0c] = 6e9
parameter[particle] = electron

qf: quadrupole, l = 0.5, k1 = 1.2
qd: quadrupole, l = 0.5, k1 = -1.1
sf: sextupole, l = 0.2, k2 = 25.0
sd: sextupole, l = 0.2, k2 = -30.0
b: sbend, l = 6.0, angle = 2*pi/60
d1: drift, l = 3.0
d2: drift, l = 1.0

cell: line = (qf, d2, sf, d1, b, d1, sd, d2, qd, d2, sd, d1, b, d1, sf, d2)
ring: line = (30*cell)
use, ring
```

### Chicane with Overlay Control
```
parameter[geometry] = open
parameter[p0c] = 1e7
beginning[beta_a] = 20
beginning[beta_b] = 20

bnd1: rbend, l = 2
bnd2: rbend, l = 2
d1: drift, l = 3
d2: drift, l = 2

chicane: overlay = {bnd1[dg]:-ge, bnd2[dg]:ge}, var = {ge}, ge = 2e-3

c_line: line = (bnd1, d1, bnd2, d2, bnd2, d1, bnd1)
use, c_line
```

### Energy Recovery Linac (Multipass)
```
parameter[geometry] = open
bmad_com[absolute_time_tracking] = T

bend_l1: sbend, angle = -25*pi/180, l = 0.2
bend_l2: bend_l1
a_patch: patch, flexible = T
d_patch: patch, x_offset = 0.034, x_pitch = asin(0.32)
inject: line = (...)
linac: line[multipass] = (bend_l1, ..., bend_l2)
arc: line = (...)
dump: line = (...)

erl: line = (inject, linac, arc, a_patch, linac, d_patch, dump)
use, erl
```

### Colliding Beam Dual Ring
```
ir: line[multipass] = (...)
pa_in: patch, ...
pa_out: patch, ...
pb_in: patch, ...
pb_out: patch, ...
m: marker
fid: fiducial, origin_ele = m

A: line = (arc_a, pa_in, ir, m, pa_out)
A[particle] = electron
B_rev: line = (arc_b, pb_in, ir, fid, pb_out)
B: line = (--B_rev)
B[particle] = Au+79
use, A, B
```

## When to Load Reference Files

The information above covers common Bmad usage. For specific tasks, load the appropriate
reference file **before** answering or writing code.

### `references/elements.md`
**Load when:**
- User asks about a specific element type not fully described above (e.g., `wiggler`, `crystal`, `ac_kicker`, `converter`, `em_field`)
- You need the full attribute list for an element (what parameters does `lcavity` accept?)
- You need to choose the right element type for a given physics scenario
- User asks about photon/X-ray elements (`crystal`, `mirror`, `multilayer_mirror`, `diffraction_plate`, `sample`)

### `references/attributes.md`
**Load when:**
- User asks about apertures, collimation, or beam pipe geometry
- User asks about field maps (`cartesian_map`, `cylindrical_map`, `grid_field`, `gen_grad_map`)
- User asks about misalignments, offsets, pitch, tilt, or `girder` orientation
- User asks about `field_master`, normalized vs. unnormalized field strengths
- User asks about wake fields (short-range or long-range)
- User asks about multipole errors (`a0`..`a21`, `b0`..`b21`) or scaling (`r0_mag`, `r0_elec`)
- You need to know which attributes apply to which element types

### `references/lattice-syntax.md`
**Load when:**
- User asks about superposition (`superimpose`, overlapping elements, `super_lord`/`super_slave`)
- User asks about multipass (ERLs, `line[multipass]`, `phi0_multipass`)
- User asks about beam initialization (`beam_init_struct`, particle distributions, reading beam files)
- User asks about `expand_lattice` or post-expansion operations
- User asks about custom attributes (`parameter[custom_attributeN]`)
- User asks about `bmad_com` settings or parameter structures
- User asks about converting lattices to/from MAD, SAD, or Elegant
- User asks about `fork`, `photon_fork`, branching, or multi-branch lattices

### `references/physics-conventions.md`
**Load when:**
- User asks about coordinate systems, reference orbit construction, or global floor coordinates
- User asks about phase space coordinate definitions or how `z` and `pz` work
- User asks about electromagnetic field conventions, multipole expansions, or field scaling formulas
- User asks about Twiss parameters, coupling, normal modes, or dispersion in detail
- User asks about synchrotron radiation, radiation integrals, damping, or equilibrium emittance
- User asks about fringe field models (hard-edge, soft-edge, bend/quad fringes)
- User asks about spin dynamics or the T-BMT equation
- User asks about wake field physics or CSR/space charge

### `references/tracking-methods.md`
**Load when:**
- User asks which tracking methods are available for a specific element type
- User asks about `runge_kutta` step size control, tolerances, or adaptive stepping
- User asks about `symp_lie_ptc` or PTC integration (single-element vs. whole-lattice mode)
- User asks about `mat6_calc_method` or transfer matrix calculation options
- User asks about spin tracking methods
- User asks about Taylor maps, map orders, or symplectification
- User asks about X-ray/photon tracking (coherent vs. incoherent)
- User asks about `absolute_time_tracking`, `field_calc`, or simulation measurement modules
