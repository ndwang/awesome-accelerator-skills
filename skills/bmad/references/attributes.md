# Bmad Element Attributes Reference

## Table of Contents

1. [Dependent vs Independent Attributes](#dependent-vs-independent-attributes)
2. [Field_Master and Normalized vs Unnormalized Strengths](#field_master-and-normalized-vs-unnormalized-strengths)
3. [Orientation and Misalignment Attributes](#orientation-and-misalignment-attributes)
4. [Aperture and Limit Attributes](#aperture-and-limit-attributes)
5. [Multipole Attributes](#multipole-attributes)
6. [Field Map Attributes](#field-map-attributes)
7. [Wake Field Attributes](#wake-field-attributes)
8. [Wall and Chamber Attributes](#wall-and-chamber-attributes)
9. [Fringe Field Control Attributes](#fringe-field-control-attributes)
10. [Common Attributes](#common-attributes)
11. [Element-to-Attribute Reference Table](#element-to-attribute-reference-table)

---

## Dependent vs Independent Attributes

Bmad computes some attributes automatically from others. The computed values are "dependent" and the ones you set are "independent." You cannot directly set a dependent attribute in the lattice file.

| Element              | Independent Variables                  | Dependent Variables              |
|----------------------|----------------------------------------|----------------------------------|
| All elements         | `ds_step`                              | `num_steps`                      |
| `BeamBeam`           | `charge`, `sig_x`, `sig_y`, `e_tot`   | `bbi_constant`                   |
| `Elseparator`        | `hkick`, `vkick`, `gap`, `l`, `e_tot`  | `e_field`, `voltage`            |
| `Lcavity`            | `gradient`, `l`                        | `e_loss`, `voltage`              |
| `Rbend`, `Sbend`     | `g`, `l`                               | `rho`, `angle`, `l_chord`        |
| `Wiggler` (map)      | `term(i)`                              | `b_max`, `k1`, `rho`            |
| `Wiggler` (periodic) | `b_max`, `e_tot`                       | `k1`, `rho`                      |

---

## Field_Master and Normalized vs Unnormalized Strengths

The `field_master` attribute controls whether an element's normalized (by reference energy) or unnormalized field strengths are the independent variables.

- **Default `field_master = False`**: Normalized strengths (e.g., `k1`, `g`) are independent.
- **`field_master = True`**: Unnormalized (absolute) field strengths (e.g., `b1_gradient`, `b_field`) are independent.

The default is inferred from what you set: if you set unnormalized values, `field_master` defaults to True.

| Element                        | Normalized    | Unnormalized     |
|--------------------------------|---------------|------------------|
| `Sbend`, `Rbend`               | `g`           | `b_field`        |
| `Sbend`, `Rbend`               | `dg`          | `db_field`       |
| `Solenoid`, `Sol_quad`         | `ks`          | `bs_field`       |
| `Quadrupole`, `Sol_quad`, bends| `k1`          | `b1_gradient`    |
| `Sextupole`, bends             | `k2`          | `b2_gradient`    |
| `Octupole`                     | `k3`          | `b3_gradient`    |
| `HKicker`, `VKicker`           | `kick`        | `bl_kick`        |
| Most elements                  | `hkick`       | `bl_hkick`       |
| Most elements                  | `vkick`       | `bl_vkick`       |

You cannot mix normalized and unnormalized in the same element definition:

```
Q1: quadrupole, b1_gradient = 0   ! field_master defaults to True
Q2: quadrupole, k1 = 0.6          ! field_master defaults to False
Q3: quadrupole, k1 = 0.6, bl_hkick = 37.5  ! ERROR: cannot mix
```

---

## Orientation and Misalignment Attributes

Orientation attributes shift and rotate physical elements relative to the reference orbit. There are seven element classes with different orientation rules.

### Straight Line Elements

Includes quadrupoles, sextupoles, markers, and most non-bend elements.

```
x_offset = <Real>   ! Transverse x displacement [m]
y_offset = <Real>   ! Transverse y displacement [m]
z_offset = <Real>   ! Longitudinal displacement [m]
x_pitch  = <Real>   ! Rotation about y-axis [rad]
y_pitch  = <Real>   ! Rotation about neg. x-axis [rad]
tilt     = <Real>   ! Rotation about z-axis [rad]
```

- Offsets translate the element. Pitches rotate about the element center.
- `tilt` without a value gives a skew element: default is pi/(2*(n+1)) where n is the element order (n=1 for quad, n=2 for sextupole, etc.).
- These do NOT affect the reference orbit.
- Comparison with MAD: `x_pitch` (Bmad) = `dtheta` (MAD), `y_pitch` (Bmad) = `-dphi` (MAD).

### Bend Elements (Sbend, Rbend, RF_Bend)

Bends use `roll` instead of `tilt`, plus `ref_tilt`:

```
x_offset = <Real>   ! Same as straight elements
y_offset = <Real>
z_offset = <Real>
x_pitch  = <Real>
y_pitch  = <Real>
ref_tilt = <Real>   ! Rotates BOTH element AND reference orbit
roll     = <Real>   ! Rotates element only (like tilt for bends)
```

- `roll` rotates the bend about the entrance-to-exit axis. Does NOT affect reference orbit.
- `ref_tilt` rotates both element and reference orbit. A `ref_tilt` of pi/2 bends vertically. Do NOT use `ref_tilt` for misalignment studies.

### Girder-Supported Elements

When elements sit on a `girder`, their offsets/pitches are relative to the girder. The total computed offsets are stored in dependent `*_tot` attributes:

```
x_offset_tot, y_offset_tot, z_offset_tot
x_pitch_tot, y_pitch_tot, tilt_tot, roll_tot
```

If no girder, `*_tot` equals the corresponding non-`_tot` value.

### Random Misalignment

```
quadrupole::bnd10:bnd20[y_offset] = 1.4e-6*ran_gauss(5)
```

---

## Aperture and Limit Attributes

```
x1_limit = <Real>      ! Negative-x half-width [m]
x2_limit = <Real>      ! Positive-x half-width [m]
y1_limit = <Real>      ! Negative-y half-width [m]
y2_limit = <Real>      ! Positive-y half-width [m]
x_limit  = <Real>      ! Sets x1_limit = x2_limit
y_limit  = <Real>      ! Sets y1_limit = y2_limit
aperture = <Real>      ! Sets all four limits to one value
aperture_at   = <Switch>
aperture_type = <Switch>
offset_moves_aperture = <Logical>
```

A zero limit value means no aperture in that plane. The `x_limit`, `y_limit`, and `aperture` shortcuts are NOT stored internally -- always reference `x1_limit` etc. in expressions.

### Aperture Types

```
auto         ! Default for detector, mask, diffraction_plate
elliptical   ! Default for ecollimator
rectangular  ! Default for most elements
wall3d       ! Uses vacuum chamber wall geometry
custom       ! User-supplied code
```

### Aperture Placement (`aperture_at`)

```
exit_end       ! Default for most elements
entrance_end
both_ends
continuous     ! Checked at every integration step
no_aperture
surface        ! Default for crystal, mirror, detector, etc.
wall_transition ! Particle lost only when crossing wall boundary
```

### Aperture and Offsets

By default, apertures are independent of element offsets. Set `offset_moves_aperture = T` to have offsets shift the aperture. Exceptions: `rcollimator`, `ecollimator`, `mirror`, `multilayer_mirror`, `crystal` default to True.

```
q1: quad, l = 0.6, x1_limit = 0.045, offset_moves_aperture = T
```

---

## Multipole Attributes

### Multipole Element (KnL/Tn representation)

For `multipole` elements, fields use integrated strength with tilt:

```
KnL  = <Real>   ! Normal integrated strength, n = 0..21
KnSL = <Real>   ! Skew integrated strength
Tn   = <Real>   ! Tilt for n-th order. Default: pi/(2n+2) for skew
```

```
m: multipole, k1l = 0.32, t1   ! Skew quadrupole
```

A nonzero `K0L` (dipole) affects the reference orbit.

### AB_Multipole Element (An/Bn representation)

For `ab_multipole` elements:

```
An = <Real>   ! Skew component, n = 0..21
Bn = <Real>   ! Normal component, n = 0..21
```

There is an n-factorial difference between An/Bn and KnL/KnSL conventions.

### Multipoles on Other Elements

Elements like quadrupoles and sextupoles accept `a0`-`a20`, `b0`-`b20` for magnetic multipole errors, and `a0_elec`-`a21_elec`, `b0_elec`-`b21_elec` for electric multipoles.

For non-multipole elements, magnetic multipoles are scaled by the element strength:

```
a_n(actual) = F * (r0^n_ref / r0^n) * a_n(input)
```

where F is the element strength and `r0` is set by `r0_mag`. Set `scale_multipoles = F` to disable scaling.

```
q1: quadrupole, b2 = 0.12, a20 = 1e7, scale_multipoles = F
```

Electric multipoles use `r0_elec` for scaling but are never scaled by element strength.

### multipoles_on

Toggle multipole errors on/off without removing them:

```
quadrupole::*[multipoles_on] = False
```

This only affects An/Bn multipoles, not the primary field (e.g., `k1` of a quadrupole).

---

## Field Map Attributes

Four types of field maps for complex EM field configurations:

```
cartesian_map    ! DC fields, Laplace solutions in Cartesian coords
cylindrical_map  ! DC or AC fields, Laplace solutions in cylindrical coords
grid_field       ! Field on a grid with interpolation
gen_grad_map     ! Generalized gradients (DC only)
```

Field maps require integration-type tracking (`field_calc = fieldmap`). They are ignored by `bmad_standard` tracking. Multiple maps sum their fields.

### Common Field Map Attributes

- `field_scale`: Overall amplitude multiplier (default 1).
- `master_parameter`: Element attribute that scales the field (e.g., `"K1"`).
- `ele_anchor_pt`: Origin reference -- `beginning` (default), `center`, or `end`.
- `r0 = (x0, y0, z0)`: Offset of field origin from anchor point.
- `field_type`: `magnetic`, `electric`, or `mixed` (grid_field only).
- `curved_ref_frame`: For bends, use curvilinear coords (grid_field and gen_grad_map only).

### Cartesian Map Example

```
q01: quadrupole, l = 0.6, field_calc = fieldmap,
  cartesian_map = {
    field_type = magnetic,
    term = {0.03, 3.00, 4.00, 5.00, 0, 0, 0.63, y},
    term = {...}, ...
  }
```

### Cylindrical Map Example

```
m1: lcavity, rf_frequency = 1e6, field_calc = fieldmap,
  cylindrical_map = {
    m = 2, harmonic = 3, dz = 0.1,
    r0 = (0, 0, 0.001),
    ele_anchor_pt = center, master_parameter = voltage,
    e_coef_re = (...), e_coef_im = (...),
    b_coef_re = (...), b_coef_im = (...) }
```

### Grid Field Example

```
apex: e_gun, l = 0.23, field_calc = fieldmap, rf_frequency = 187e6,
  grid_field = call::apex_gun_grid.bmad
```

Grid geometries: `rotationally_symmetric_rz` or `xyz`. Interpolation order: 1 (linear, default) or 3 (cubic). Grids can be stored in HDF5 format.

### Gen_Grad_Map Example

```
t1: sbend, k1 = 2, field_calc = fieldmap,
  gen_grad_map = {
    field_type = electric, ele_anchor_pt = end,
    dz = 1.2, r0 = (0, 0, 2.0), field_scale = 1.3,
    master_parameter = k1, curved_ref_frame = False,
    curve = {
      m = 1, kind = cos,
      derivs = {
        0.0: 0.1 0.02 0.003,
        1.2: 0.11 0.021 0.0031,
        ...
      }
    }
  }
```

### Modifying Field Maps After Definition

```
qq[grid_field(1)%field_scale] = 0.7
qq[grid_field(1)%master_parameter] = k1
```

---

## Wake Field Attributes

### Short-Range Wakes

Specified via pseudo-modes with the `sr_wake` attribute:

```
cav9: lcavity, ..., sr_wake = {
  z_max = 1.3e-3, scale_with_length = F,
  longitudinal = {3.23e14, 1.23e3, 3.62e3, 0.123, none},
  transverse = {4.23e14, 2.23e3, 5.62e3, 0.789, none, trailing}
}
```

Longitudinal mode components: amplitude [V/C/m], damping [1/m], wavenumber [1/m], phase [rad/2pi], position_dependence (`none`, `x_leading`, `y_leading`, `x_trailing`, `y_trailing`).

Transverse mode components: amplitude [V/C/m^2], damping, wavenumber, phase, polarization (`none`, `x_axis`, `y_axis`), particle_dependence (`none`, `leading`, `trailing`).

Additional parameters: `z_max` (validity range), `z_scale`, `amp_scale`, `scale_with_length`.

A `z_long` sub-structure allows specifying the longitudinal wake as a table of (z, w) points.

### Long-Range Wakes

Specified with the `lr_wake` attribute:

```
cav9: lcavity, ..., lr_wake = {
  freq_spread = 0.001,
  mode = {1.65e9, 0.76, 1.18e4, 0, 1, unpolarized},
  mode = {-1, 0.57, 3e4, 0, 2, 0.15}
}
```

Mode components: frequency [Hz], R/Q [Ohm/m^(2m)], damping, phase [rad/2pi], m-order, polarization angle.

A negative frequency locks the mode to `rf_frequency`. Additional parameters: `time_scale`, `amp_scale`, `freq_spread`, `self_wake_on`, `t_ref`.

---

## Wall and Chamber Attributes

The `wall` attribute defines vacuum chamber walls, capillary inside walls, or diffraction_plate/mask geometry. Walls are built from cross-sectional slices:

```
ele_name: capillary, wall = {
  section = {
    s = 0,
    v(1) = {0.02, 0.00},
    v(2) = {0.00, 0.02, 0.02},
    v(3) = {-0.01, 0.01}
  },
  section = {
    s = 0.34,
    v(1) = {0.003, -0.001, 0.015, 0.008, 0.2*pi}
  }
}
```

Each vertex `v(j) = {x, y, radius_x, radius_y, tilt}`:
- `radius_x = 0, radius_y = 0`: straight line segment
- `radius_x != 0, radius_y = 0`: circular arc
- `radius_x != 0, radius_y != 0`: elliptical arc

Vertices must be arranged counter-clockwise. Mirror symmetry is auto-detected from vertex coordinates.

Vacuum chamber walls interpolate between cross-sections and can extend across multiple elements. Section `type` values for crotch geometry: `normal`, `leg1`, `leg2`, `trunk1`, `trunk2`, `trunk`.

For `diffraction_plate` and `mask` elements, sections have type `clear` or `opaque` to define transmission regions.

---

## Fringe Field Control Attributes

### fringe_at

Controls which ends have fringe fields:

```
no_end
both_ends        ! Default
entrance_end
exit_end
```

### fringe_type

Selects the fringe field model:

```
none              ! No fringe
soft_edge_only    ! Linear part only
hard_edge_only    ! Zero-length limit
full              ! Full fringe model
linear_edge       ! Bends only: linear dipole hard edge
basic_bend        ! Bends only: second-order (default for bends)
sad_full          ! SAD-compatible full fringe
```

Default: `basic_bend` for bends, `full` for lcavity/rfcavity/e_gun, `none` for all others.

### Additional Fringe Parameters

- `spin_fringe_on`: Enable spin tracking through fringes (default True).
- `fint`, `fintx`: Field integral parameters for bend fringe fields.
- `hgap`, `hgapx`: Half-gap of bend magnet for fringe calculation.
- `fq1`, `fq2`: Quadrupole soft-edge fringe parameters.
- `ptc_fringe_geometry`: For PTC tracking -- `x_invariant` or `multipole_symmetry`.

```
b1: rbend, angle = pi/4, g = 0.3, fringe_type = full
q: quad, spin_fringe_on = T, fringe_at = exit_end
```

---

## Common Attributes

### Length

```
l           = <Real>   ! Path length [m] (chord length for rbend input)
l_chord     = <Real>   ! Chord length of a bend (dependent)
l_rectangle = <Real>   ! Rectangular length for bends
```

For `patch` elements, `l` equals `z_offset` (dependent). For `girder`, `l` is computed from supported elements. For `capillary`, `l` is the `s` of the last wall section.

### Is_On

```
is_on = <Logical>   ! Turns element off (makes it act as a drift)
```

Does NOT affect apertures, reference orbit, or reference energy. Cannot turn off: `drift`, `crystal`, `mirror`, `patch`, `fiducial`, etc.

### Type, Alias, and Descrip

```
type    = "<String>"   ! Up to 40 characters
alias   = "<String>"   ! Up to 40 characters
descrip = "<String>"   ! Up to 200 characters
```

Used for labeling and pattern matching. Not converted to upper case.

```
Q00W: Quad, type = "My Type", alias = Who_knows, descrip = "Only the shadow knows"
```

### Tracking and Calculation Methods

```
tracking_method      = <Method>   ! How particles are tracked
mat6_calc_method     = <Method>   ! How transfer matrices are calculated
spin_tracking_method = <Method>   ! How spin is tracked
field_calc           = <Switch>   ! fieldmap or bmad_standard
```

### Integration Control

```
ds_step          = <Real>   ! Step size for integration
num_steps        = <Int>    ! Number of steps (dependent on ds_step)
integrator_order = <Int>    ! Order of the Runge-Kutta integrator
```

### Reference Energy

```
e_tot   = <Real>   ! Total energy [eV] (dependent for most elements)
p0c     = <Real>   ! Momentum * c [eV] (dependent for most elements)
```

Set at the lattice start via `beginning[e_tot]` or `parameter[p0c]`.

### Superposition

```
superimpose           ! Superimpose element on the lattice
create_jumbo_slave    ! Control superposition slave creation
wrap_superimpose      ! Allow wrapping around lattice ends
```

### Other Common

```
symplectify                  = <Logical>  ! Apply symplectification
taylor_map_includes_offsets  = <Logical>  ! Include offsets in Taylor map
multipoles_on                = <Logical>  ! Toggle multipole errors
ref_time_start               = <Real>     ! Reference time at entrance [sec]
delta_ref_time               = <Real>     ! Change in reference time [sec]
```

---

## Element-to-Attribute Reference Table

Summary of which attribute groups apply to which element types. "Y" = has the attribute group.

| Element Type        | Orientation | Aperture | Multipoles | Field Maps | Wakes | Wall | Fringe | field_master |
|---------------------|:-----------:|:--------:|:----------:|:----------:|:-----:|:----:|:------:|:------------:|
| AB_Multipole        | partial     | Y        | a/b only   |            |       | Y    |        | Y            |
| AC_Kicker           | Y           | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| BeamBeam            | Y           | Y        |            |            |       | Y    |        |              |
| Rbend, Sbend        | Y (roll)    | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| Crab_Cavity         | Y           | Y        | Y          | Y          | Y     | Y    |        | Y            |
| Crystal             | Y           | Y        |            |            |       | Y    |        |              |
| Drift               | Y           | Y        |            |            |       | Y    |        |              |
| Ecollimator, Rcoll. | Y           | Y        |            |            | Y     | Y    | Y      |              |
| ELSeparator         | Y           | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| EM_Field            | Y           | Y        |            | Y          | Y     | Y    | Y      |              |
| E_Gun               | Y           | Y        |            | Y          | Y     | Y    | Y      |              |
| Kicker              | Y           | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| HKicker, VKicker    | Y           | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| Lcavity             | Y           | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| Marker              | Y           | Y        |            |            | Y     | Y    |        |              |
| Monitor, Instrument | Y           | Y        |            |            | Y     | Y    | Y      |              |
| Multipole           | partial     | Y        | knl/tn     |            |       | Y    |        | Y            |
| Octupole            | Y           | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| Quadrupole          | Y           | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| RFCavity            | Y           | Y        | Y          | Y          | Y     | Y    | Y      |              |
| RF_Bend             | Y (roll)    | Y        |            | partial    | Y     | Y    | Y      | Y            |
| Sextupole           | Y           | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| Solenoid            | Y           | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| Sol_Quad            | Y           | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| Taylor              | Y           | Y        |            |            |       | Y    |        |              |
| Thick_Multipole     | Y           | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| Wiggler, Undulator  | Y           | Y        | Y          | Y          | Y     | Y    | Y      | Y            |
| Group               |             |          |            |            |       |      |        |              |
| Overlay             |             |          |            |            |       |      |        |              |
| Ramper              |             |          |            |            |       |      |        |              |
| Girder              | Y           |          |            |            |       |      |        |              |
| Fork, Photon_Fork   |             | Y        |            |            |       |      |        |              |
| Patch               | Y           | Y        |            |            |       | Y    |        |              |
| Fiducial            | special     |          |            |            |       |      |        |              |

Notes:
- "partial" orientation = has offsets/tilt but not full pitch set.
- "Y (roll)" = uses `roll` instead of `tilt` for bends.
- "a/b only" = uses An/Bn directly, not as errors on a primary field.
- "knl/tn" = uses KnL/Tn representation.
- Control elements (Group, Overlay, Ramper) have only `alias`, `descrip`, `type`, `is_on`, and controller-specific attributes.
- Nearly all physical elements have `l`, `is_on`, `type`, `alias`, `descrip`, `tracking_method`, `mat6_calc_method`, `spin_tracking_method`, `e_tot`, `p0c`, and `superimpose`.
