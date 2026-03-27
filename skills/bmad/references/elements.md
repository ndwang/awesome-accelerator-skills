# Bmad Lattice Elements Reference

## Table of Contents

- [Overview](#overview)
- [Bends](#bends)
- [Quadrupoles and Multipoles](#quadrupoles-and-multipoles)
- [Thin Multipoles](#thin-multipoles)
- [RF Cavities](#rf-cavities)
- [Kickers](#kickers)
- [Drifts, Markers, and Passive Elements](#drifts-markers-and-passive-elements)
- [Collimators and Apertures](#collimators-and-apertures)
- [Geometry and Coordinate Elements](#geometry-and-coordinate-elements)
- [Branching Elements](#branching-elements)
- [Control Elements](#control-elements)
- [Special Particle Elements](#special-particle-elements)
- [Photon Elements](#photon-elements)
- [Map and Custom Elements](#map-and-custom-elements)

---

## Overview

Bmad elements fall into three groups: **particle elements** (charged particle tracking), **photon elements** (x-ray optics), and **control elements** (parameter control of other elements). Some elements (e.g., `drift`, `marker`, `fork`) work with both particles and photons.

---

## Bends

### Sbend / Rbend

Dipole bend magnets. `rbend` uses rectangular (chord) coordinates; `sbend` uses sector (arc) coordinates. All `rbend` elements are converted to `sbend` internally.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `l` | Real | -- | Arc length (sbend) or chord length (rbend) |
| `angle` | Real | dep. | Design bend angle |
| `g` | Real | -- | Bend strength = 1/rho |
| `dg` | Real | 0 | Actual - design strength difference |
| `e1`, `e2` | Real | 0 | Entrance/exit face angles |
| `k1`, `k2` | Real | 0 | Quadrupole/sextupole strength |
| `fint`, `fintx` | Real | 0 | Fringe field integrals |
| `hgap`, `hgapx` | Real | 0 | Pole half-gap |
| `ref_tilt` | Real | 0 | Rotation about longitudinal axis |
| `exact_multipoles` | Switch | `off` | `off`, `vertically_pure`, `horizontally_pure` |
| `fiducial_pt` | Switch | `none` | `none`, `entrance_end`, `center`, `exit_end` |

```bmad
b03w: sbend, l = 0.6, k1 = 0.003, fint
my_rb: rbend, l = 0.54, g = 1.52, e1 = 0.1, e2 = 0.1
```

**Notes:** `g`, `angle`, `l` are mutually dependent (set any two). Changing `g` moves downstream elements; use `dg` for errors. `ref_tilt` bends the reference orbit -- use `roll` for misalignment. An sbend with `e1 = e2 = angle/2` equals an rbend with `e1 = e2 = 0`.

### RF_Bend

RF cavity with sbend geometry. **Experimental.** Tracking limited to Runge-Kutta; fields via grid maps.

```bmad
rfb: rf_bend, l = 0.5, g = 0.1, rf_frequency = 500e6, phi0 = 0.25
```

---

## Quadrupoles and Multipoles

### Quadrupole

Linear transverse field. Positive `k1` (zero tilt) = horizontally focusing.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `k1` | Real | 0 | Normalized strength |
| `b1_gradient` | Real | dep. | Unnormalized field |
| `tilt` | Real | 0 | Bare `tilt` keyword defaults to pi/4 |
| `fq1`, `fq2` | Real | 0 | Soft edge fringe parameters |

```bmad
q03w: quad, l = 0.6, k1 = 0.003, tilt  ! tilt defaults to pi/4
```

### Sextupole

Quadratic field dependence. Kick-drift-kick model. Bare `tilt` defaults to pi/6.

```bmad
sx1: sext, l = 0.6, k2 = 0.3, tilt
```

### Octupole

Cubic field dependence. Kick-drift-kick model. Bare `tilt` defaults to pi/8.

```bmad
oct1: octupole, l = 4.5, k3 = 0.003, tilt
```

### Thick_Multipole

Like sextupole/octupole but uses `a0..a21`, `b0..b21` multipoles directly (no dedicated `k2`/`k3`).

```bmad
tm1: thick_multipole, l = 4.5, a7 = 1.23e3, b8 = 7.54e5
```

### Solenoid

Longitudinal magnetic field. Default: hard-edge model. For soft-edge fringes, set `field_calc = soft_edge` with Runge-Kutta tracking.

| Attribute | Type | Description |
|-----------|------|-------------|
| `ks` | Real | Normalized solenoid strength |
| `bs_field` | Real | Field strength |
| `l_soft_edge` | Real | Soft edge fringe length |
| `r_solenoid` | Real | Solenoid radius (soft edge) |

```bmad
cleo_sol: solenoid, l = 2.6, ks = 1.5e-9 * parameter[p0c]
```

### Sol_Quad

Combined solenoid + quadrupole. Attributes: `k1`, `ks`, `bs_field`, `b1_gradient`.

```bmad
sq02: sol_quad, l = 2.6, k1 = 0.632, ks = 1.5e-9*parameter[p0c]
```

---

## Thin Multipoles

### AB_Multipole

Thin multipole (up to order 21) using `a0..a21`, `b0..b21`. Length is fictitious (affects s-position, not tracking). Does NOT bend reference orbit with dipole component. Zero length when superimposed.

```bmad
abc: ab_multipole, a2 = 0.034e-2, b3 = 5.7, a11 = 5.6e6/2
```

### Multipole

Thin multipole using `K0L..K21L`, `K0SL..K21SL`, `T0..T21` notation.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `K0L_status` | Switch | `not_allowed` | `not_allowed`, `bends_reference`, `straight_reference` |

```bmad
m1: multipole, k1l = 0.034e-2, t1, k3sl = 4.5, t3 = 0.31*pi
```

**Notes:** `K0L` disabled by default. `bends_reference` = MAD-compatible (shifts downstream elements). `straight_reference` = PTC-compatible (simple dipole kick).

---

## RF Cavities

### RFcavity

Storage ring cavity. Reference energy is constant. Energy kick: `dE = -e_charge * r_q * voltage * sin(2*pi*(phi_t - phi_ref))`.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `voltage` | Real | 0 | Cavity voltage (V) |
| `rf_frequency` | Real | 0 | Frequency (Hz) |
| `harmon` | Real | 0 | Harmonic number |
| `phi0` | Real | 0 | Phase (rad/2pi). 0 = on crest |
| `cavity_type` | Switch | `standing_wave` | `standing_wave`, `traveling_wave`, `ptc_standard` |

```bmad
rf1: rfcav, l = 4.5, harmon = 1281, voltage = 5e6
```

**Notes:** MAD `lag` to Bmad: `phi0 = lag + 0.5`. If `harmon` is set, `rf_frequency` is computed from lattice length.

### Lcavity

LINAC cavity. Reference energy changes. Energy kick: `dE = r_q * gradient_tot * L * cos(2*pi*(phi_t + phi_ref))`.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `gradient` | Real | 0 | Gradient (V/m) |
| `gradient_err` | Real | 0 | Gradient error |
| `voltage` | Real | dep. | = gradient * l |
| `rf_frequency` | Real | 0 | Frequency (Hz) |
| `phi0` | Real | 0 | Phase (rad/2pi). 0 = on crest |
| `e_loss` | Real | 0 | Short-range wake loss (V/C) |
| `n_cell` | Int | -1 | Number of cells (-1 = auto) |
| `cavity_type` | Switch | `standing_wave` | Type of cavity |

```bmad
lwf: lcavity, l = 2.3, rf_frequency = 500e6, voltage = 20e6
```

**Notes:** Transfer matrix is never symplectic when reference energy changes.

### Crab_Cavity

RF cavity giving z-dependent transverse kick for crossing angle compensation.

```bmad
cc1: crab_cavity, l = 0.5, gradient = 1e6, rf_frequency = 500e6
```

Key attributes: `gradient`, `voltage` (dep.), `rf_frequency`, `phi0`, `harmon`.

---

## Kickers

### Kicker

Deflects beam in both planes. Uses `hkick`/`vkick` attributes plus `h_displace`/`v_displace`.

```bmad
a_kick: kicker, l = 4.5, hkick = 0.003
```

### HKicker / VKicker

Single-plane kickers using the `kick` attribute (not `hkick`/`vkick`).

```bmad
h_kick: hkicker, l = 4.5, kick = 0.003
```

### AC_Kicker

Time-dependent kicker. Field scaled by amplitude function A(delta_t). Specify waveform via `amp_vs_time` (time-amplitude pairs) or `frequencies` (freq, amp, phi triplets; phi in rad/2pi).

```bmad
mk: ac_kicker, l = 0.3, b1 = 0.27, t_offset = 3.6e-8,
        amp_vs_time = {(-1.2e-6, 0.02), (1.2e-6, 0.03)}
```

**Notes:** Fields obey Maxwell only when omega << c/r (slow variation limit).

### GKicker

Zero-length general kicker displacing a particle in all six phase space dimensions: `x_kick`, `px_kick`, `y_kick`, `py_kick`, `z_kick`, `pz_kick`.

```bmad
gk: gkicker, x_kick = 0.003, pz_kick = 0.12
```

---

## Drifts, Markers, and Passive Elements

### Drift

Field-free space. Cannot have chamber walls (use `pipe` instead). Drifts disappear when superimposed upon.

```bmad
d21: drift, l = 4.5
```

### Marker

Zero-length position marker. Identity transfer map. Offset/tilt not used by Bmad (available for program use, e.g. BPM offsets).

```bmad
mm: mark, type = "BPM"
```

### Pipe / Instrument / Monitor

Behave like drifts but persist through superposition. Use `pipe` when a field-free region needs a chamber wall.

```bmad
d21: instrum, l = 4.5
```

### Null_Ele

Like a marker but removed during lattice expansion. Useful for superposition reference points.

```bmad
N: null_ele, superimpose, ref = quadrupole::*
```

### Beginning_Ele

Automatically placed at index 0 of every branch. Not user-definable elsewhere. Set attributes via `beginning` or line parameter statements.

---

## Collimators and Apertures

### Ecollimator / Rcollimator

Drift with elliptic (`ecollimator`) or rectangular (`rcollimator`) collimation. Can also limit px, py, z, pz coordinates via `px_aperture_width2`, etc.

```bmad
d21: ecollimator, l = 4.5, x_limit = 0.09, y_limit = 0.05
```

**Notes:** Aperture rotates with `tilt` (exception to normal rule). Default `offset_moves_aperture = True`.

### Mask

Zero-length element with arbitrary-shape aperture defined via wall geometry.

```bmad
scrapper: mask, mode = transmission, wall = {
    section = {type = clear, v(1) = {0.9, 0.5}},
    section = {type = opaque, r0 = (0, 0.4), v(1) = {0.1, 0.1}} }
```

---

## Geometry and Coordinate Elements

### Patch

Shifts reference orbit and/or time. Generalized drift with arbitrary entrance-to-exit orientation.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `x_offset`, `y_offset`, `z_offset` | Real | 0 | Exit face offset |
| `x_pitch`, `y_pitch`, `tilt` | Real | 0 | Exit face orientation |
| `t_offset` | Real | 0 | Reference time offset |
| `E_tot_offset` | Real | 0 | Reference energy offset (eV) |
| `E_tot_set`, `p0c_set` | Real | 0 | Set exit energy/momentum |
| `flexible` | Logical | False | Adapts to surrounding geometry |
| `ref_coords` | Switch | `exit_end` | `exit_end` or `entrance_end` |

```bmad
pt: patch, z_offset = 3.2       ! Like a drift
pt2: patch, E_tot_offset = 1e6  ! Energy change
```

**Notes:** When both orbit and energy need patching, use two separate patches. A `flexible` patch adapts geometry to match the downstream element.

### Floor_Shift

Shifts reference orbit in global coordinates without affecting tracking. Identity transfer map. Only affects downstream elements.

```bmad
floor: floor_shift, z_offset = 3.2
```

### Fiducial

Fixes reference orbit position/orientation in global coordinates. Affects elements both upstream and downstream. For tracking, acts as zero-length marker. At most one per branch (unless separated by flexible patches).

```bmad
f1: fiducial, origin_ele = mark1, dx_origin = 0.04
```

### Fixer

Sets orbit and Twiss parameters at any point in an open-geometry branch. **Under construction.** Only one can be active per branch. No effect in closed geometry.

```bmad
f2: fixer, beta_a_stored = 11.37, beta_b_stored = 34.72, is_on = T
```

---

## Branching Elements

### Fork / Photon_Fork

Marks the start of an alternative branch. `photon_fork` defaults to photon particle type; `fork` inherits parent branch type.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `to_line` | Name | -- | Target line |
| `to_element` | Name | auto | Element to connect to |
| `direction` | +/-1 | 1 | Particle propagation direction |
| `new_branch` | Logical | True | Create new branch? |

```bmad
pb: photon_fork, to_line = x_line
x_line: line = (x_patch, x1, x2)
x_line[p0c] = 1e3
```

**Notes:** Zero length; acts like a marker. Use `patch` elements to reorient forked branches. Set reference energy of forked-to branch via line parameter statements.

---

## Control Elements

### Overlay

Sets slave element attributes directly. Multiple overlays on the same attribute sum. Default variable value is 0.

```bmad
over1: overlay = {a_ele, b_ele:2.0}, var = {hkick}, hkick = 0.003
```

**Notes:** Overlays completely determine the controlled attribute (direct setting is overwritten). Cannot control same attribute as a `group`.

### Group

Makes delta changes to slave attributes: delta = expression(current) - expression(old).

```bmad
gr1: group = {q[k1]:a+b^2}, var = {a, b}, a = 1, old_a = 2
```

**Notes:** Can control `accordion_edge`, `start_edge`, `end_edge`, `s_position` for element positioning. Cannot control same attribute as an overlay.

### Girder

Support structure orienting attached elements in space. Drift elements in the slave list are ignored.

```bmad
g1: girder = {A, B, C}, x_offset = 0.03
g2: girder = {g1}  ! Girder supporting another girder (must come after g1)
```

### Ramper

Like overlay but for time-dependent control of large element sets. Only works with programs designed to handle rampers (e.g., `long_term_tracking`).

```bmad
ramp_e: ramper = {*[e_tot]:{4e8, 4.005e8, 4.02e8}},
              var = {time}, x_knot = {0, 0.001, 0.002}, interpolation = cubic
```

---

## Special Particle Elements

### BeamBeam

Interaction with opposing strong beam (Bassetti-Erskine formula). Key attributes: `sig_x`, `sig_y`, `sig_z`, `n_particle`, `n_slice`, `charge` (default -1 = opposite charge).

```bmad
bbi: beambeam, sig_x = 3e-3, sig_y = 3e-4, x_offset = 0.05, n_particle = 1.3e9
```

### Converter

Target plate converting particles to different species (e.g., e- to e+). Must be last in branch (except fork/marker). Requires fork for downstream connection.

```bmad
cvter: converter, species_out = positron, p0c = 3e6, distribution = {...}
```

### E_Gun

Electron gun. Must be first element in a linear branch. Always uses absolute time tracking. Default tracking: `time_runge_kutta`.

```bmad
apex: e_gun, l = 0.23, field_calc = fieldmap, rf_frequency = 187e6,
              grid_field = call::apex_gun_grid.bmad
```

Key attributes: `gradient`, `voltage` (= gradient * l), `rf_frequency` (0 for DC), `phi0`.

### ElSeparator

Electrostatic separator. Kick determined by `hkick`/`vkick`; `voltage = e_field * gap`.

```bmad
h_sep1: elsep, l = 4.5, hkick = 0.003, gap = 0.11
```

### EM_Field

General electromagnetic fields (AC/DC). Attributes: `constant_ref_energy` (default True), `polarity` (default 1.0). Created automatically during superposition when no other element class fits.

```bmad
emf: em_field, l = 1.0, polarity = -1, cartesian_map = {...}
```

### Foil

Material sheet for electron stripping with scattering and energy loss. Zero length. Scattering does not affect transfer matrix.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `material_type` | String | -- | Material (element or compound) |
| `thickness` | Real | 0 | Thickness (m) |
| `final_charge` | Int | full strip | Final charge state |
| `scatter_method` | Switch | `highland` | `highland`, `lynch_dahl`, `off` |

```bmad
stripper: foil, material_type = "Cu", thickness = 0.127, x1_edge = -0.3
```

### Sad_Mult

Emulates SAD MULT element. No RF or bend support. Step sizes computed automatically. Note: n! factor difference between SAD Kn and Bmad an/bn.

```bmad
qs1: sad_mult, l = 0.1, fringe_type = full, b2 = 0.6 / factorial(2)
```

### Wiggler / Undulator

Periodic alternating bends. Tracking is identical; difference is x-ray emission spectrum.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `b_max` | Real | 0 | Max on-axis field (T) |
| `l_period` | Real | -- | Period length |
| `n_period` | Real | dep. | Number of periods |
| `kx` | Real | 0 | Horizontal wave number |
| `polarity` | Real | 1.0 | Field scaling |
| `field_calc` | Switch | `planar_model` | `planar_model`, `helical_model`, `fieldmap` |

```bmad
wig2: wiggler, l = 1.6, b_max = 2.1, n_period = 8
wig1: wiggler, l = 1.6, field_calc = fieldmap, cartesian_map = {...}
```

**Notes:** `l_pole`/`n_pole` are deprecated; use `l_period`/`n_period`. Map type has no `bmad_standard` tracking.

---

## Photon Elements

### Crystal

Crystal for photon diffraction. Attributes: `crystal_type` (e.g. `"Si(111)"`), `b_param` (-1=Bragg, +1=Laue), `thickness`, `psi_angle`, `ref_orbit_follows` (default `bragg_diffracted`).

```bmad
crystal_ele: crystal, crystal_type = "Si(111)", b_param = -1
```

### Mirror

Reflects photons. Zero-length bend-like reference trajectory. Key attributes: `graze_angle`, `critical_angle`.

```bmad
m1: mirror, graze_angle = 0.01
```

### Multilayer_Mirror

Multiple dielectric layers for constructive interference. Abbreviation `multi` resolves to `multipole`, NOT `multilayer_mirror`.

```bmad
mm: multilayer_mirror, material_type = "W:BORON_CARBIDE", n_cell = 100,
          d1_thickness = 1e-9, d2_thickness = 1.5e-9
```

### Diffraction_Plate

Flat surface for x-ray diffraction accounting for coherent effects (unlike `mask`). Mode: `transmission` (default) or `reflection`.

```bmad
fresnel: diffraction_plate, wall = {...}
```

### Capillary

Glass tube for focusing x-ray beams. Wall defined via chamber wall syntax. Length is dependent on wall definition.

```bmad
cap1: capillary, critical_angle_factor = 30.0
```

### Detector

Grid of pixels for detecting particles and x-rays. Default `aperture_type = auto`.

```bmad
det: detector, pixel = {ix_bounds = (-4,5), iy_bounds = (-10,10), dr = (0.01, 0.01)}
```

### Photon_Init

Starting element for x-ray tracking. Defines initial photon distribution or references a physical source.

```bmad
pinit: photon_init, physical_source = "b05w", sig_E = 2.1
```

Key attributes: `E_center`, `sig_E`, `sig_x/y/z`, `sig_vx/vy`, `energy_distribution` (`gaussian`/`uniform`/`curve`), `physical_source`.

### Sample

Material sample illuminated by x-rays. **In development.** Mode: `reflection` or `transmission`.

```bmad
formula409: sample, x_limit = 10e-3, y_limit = 20e-3, mode = reflection
```

---

## Map and Custom Elements

### Taylor

Taylor map mapping input phase space (and optionally spin) to output coordinates.

Three syntax forms for terms:

```bmad
! Form 1: {out: coef, e1 e2 e3 e4 e5 e6}
mtlr: taylor, {4: 2.7, 0 0 2 0 0 1}
! Form 2: {out: coef | n1 n2 ...}
mtlr: taylor, {4: 2.73 | 336}
! Form 3: tt<out><n1><n2>... = coef
mtlr: taylor, tt4336 = 2.73
```

Key attributes: `ref_orbit`, `delta_e_ref`, `delta_ref_time`. Default is identity map. Turned-off Taylor acts as marker.

### Match

Matches Twiss parameters between two points via first-order transfer map.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `beta_a0/1`, `alpha_a0/1` | Real | 0 | Entrance/exit Twiss |
| `dphi_a`, `dphi_b` | Real | 0 | Phase advances (radians) |
| `matrix` | Switch | `standard` | `standard`, `match_twiss`, `identity`, `phase_trombone` |
| `kick0` | Switch | `standard` | `standard`, `match_orbit`, `zero` |

```bmad
mm: match, beta_a1 = 12.5, beta_b1 = 3.4, eta_x1 = 1.0, matrix = match_twiss
```

### Hybrid

Formed by programs by concatenating elements (essentially a Taylor element). Not user-definable.

### Custom

Element with user-defined properties via custom code linked with Bmad. Attributes: `val1..val12`, `delta_e_ref`.

```bmad
c1: custom, l = 3, val4 = 5.6, val12 = 0.9, descrip = "params.dat"
```

### Feedback

Lord element with input/output slaves for beam feedback. **Under development.** Requires specifically designed programs.

```bmad
fff: feedback, input_ele = bpm5, output_ele = kicker3
```
