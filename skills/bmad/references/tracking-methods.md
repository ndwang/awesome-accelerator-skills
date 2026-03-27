# Bmad Tracking, Transfer Matrix, and Spin Calculation Methods

## Table of Contents

- [Overview](#overview)
- [Setting Methods on Elements](#setting-methods-on-elements)
- [Particle Tracking Methods (tracking_method)](#particle-tracking-methods)
  - [Bmad_Standard](#bmad_standard)
  - [Runge_Kutta](#runge_kutta)
  - [Time_Runge_Kutta](#time_runge_kutta)
  - [Fixed_Step_Runge_Kutta and Fixed_Step_Time_Runge_Kutta](#fixed_step_runge_kutta-and-fixed_step_time_runge_kutta)
  - [Symp_Lie_PTC](#symp_lie_ptc)
  - [Symp_Lie_Bmad](#symp_lie_bmad)
  - [Taylor](#taylor)
  - [Linear](#linear)
  - [MAD](#mad)
  - [Custom](#custom)
- [Tracking Method Availability by Element Type](#tracking-method-availability-by-element-type)
- [Linear Transfer Map Methods (mat6_calc_method)](#linear-transfer-map-methods)
  - [Auto](#auto)
  - [Bmad_Standard (mat6)](#bmad_standard-mat6)
  - [Symp_Lie_PTC (mat6)](#symp_lie_ptc-mat6)
  - [Symp_Lie_Bmad (mat6)](#symp_lie_bmad-mat6)
  - [Taylor (mat6)](#taylor-mat6)
  - [Tracking (mat6)](#tracking-mat6)
  - [MAD (mat6)](#mad-mat6)
  - [Custom (mat6)](#custom-mat6)
- [mat6_calc_method Availability by Element Type](#mat6_calc_method-availability-by-element-type)
- [Spin Tracking Methods (spin_tracking_method)](#spin-tracking-methods)
  - [Spin Method Availability by Element Type](#spin-method-availability-by-element-type)
- [Step Size Control and Integration Parameters](#step-size-control-and-integration-parameters)
  - [ds_step and num_steps](#ds_step-and-num_steps)
  - [Runge-Kutta Adaptive Stepping](#runge-kutta-adaptive-stepping)
  - [PTC Integration Order](#ptc-integration-order)
- [field_calc Parameter](#field_calc-parameter)
- [Relative vs Absolute Time Tracking](#relative-vs-absolute-time-tracking)
- [Symplectic vs Non-Symplectic Tracking](#symplectic-vs-non-symplectic-tracking)
  - [symplectify Attribute](#symplectify-attribute)
  - [taylor_map_includes_offsets Attribute](#taylor_map_includes_offsets-attribute)
- [Taylor Maps](#taylor-maps)
  - [Taylor Map Structure](#taylor-map-structure)
  - [Spin Taylor Maps](#spin-taylor-maps)
  - [Symplectification of Matrices](#symplectification-of-matrices)
  - [Map Concatenation and Feed-Down](#map-concatenation-and-feed-down)
  - [Symplectic Integration of Maps](#symplectic-integration-of-maps)
- [X-Ray / Photon Tracking](#x-ray--photon-tracking)
  - [Coherent vs Incoherent Tracking](#coherent-vs-incoherent-tracking)
  - [Partially Coherent Simulations](#partially-coherent-simulations)
- [PTC Integration](#ptc-integration)
  - [Single-Element vs Whole-Lattice Mode](#single-element-vs-whole-lattice-mode)
  - [PTC Tracking Parameters](#ptc-tracking-parameters)
- [Simulation Modules](#simulation-modules)
  - [Orbit Measurement Simulation](#orbit-measurement-simulation)
  - [Dispersion Measurement Simulation](#dispersion-measurement-simulation)
  - [Coupling Measurement Simulation](#coupling-measurement-simulation)
  - [Phase Measurement Simulation](#phase-measurement-simulation)
- [CSR and Space Charge Methods](#csr-and-space-charge-methods)

---

## Overview

Bmad supports multiple methods for three types of calculations on a per-element basis:

1. **Particle tracking** -- computing exit-end phase space coordinates from entrance-end coordinates.
2. **Transfer matrix (Jacobian)** -- computing the 6x6 linear transfer map through an element.
3. **Spin tracking** -- computing exit-end spin orientation from entrance-end orientation.

Each is controlled by a separate attribute set on individual elements.

## Setting Methods on Elements

```
tracking_method      = <Switch>   ! Phase space tracking method
mat6_calc_method     = <Switch>   ! 6x6 transfer matrix calculation
spin_tracking_method = <Switch>   ! Spin tracking method
```

Methods can be set per element, per instance, or per element class:

```
q2: quadrupole, tracking_method = symp_lie_ptc
q2[tracking_method] = symp_lie_ptc
quadrupole::*[tracking_method] = symp_lie_ptc
```

---

## Particle Tracking Methods

### Bmad_Standard

Uses analytic formulas with the paraxial approximation. Fastest method. Field maps are **ignored** by `bmad_standard` tracking. Non-symplectic, but errors are typically small enough for most applications. Default for nearly all element types.

### Runge_Kutta

4th-order Runge-Kutta (Cash-Karp) with adaptive step size control. Accurate but slow compared to analytic methods. Non-symplectic. The adaptive stepper chooses step sizes to keep error below `rel_tol_adaptive_tracking` and `abs_tol_adaptive_tracking`. Recommended over `time_runge_kutta` unless particles can reverse longitudinal direction or start from zero momentum.

**Warning:** Custom fields that do not obey Maxwell's equations can cause the adaptive stepper to take infinitely small steps and halt.

### Time_Runge_Kutta

Uses time as the independent variable instead of the longitudinal $z$ position. Can handle particles that reverse longitudinal direction. Required for `e_gun` elements (particles start with zero momentum) and dark current simulations. Non-symplectic.

Note: `time_runge_kutta` is distinct from absolute time tracking. The former changes the integration variable; the latter changes how the RF phase is computed.

### Fixed_Step_Runge_Kutta and Fixed_Step_Time_Runge_Kutta

Same as their adaptive counterparts but use fixed step sizes set by `ds_step` or `num_steps`. Generally much less efficient than adaptive stepping. Non-symplectic. Use only when there is a compelling reason to avoid adaptive control.

### Symp_Lie_PTC

Symplectic tracking using Hamiltonian with Lie operator techniques via Etienne Forest's PTC library. Accurate and symplectic but slow. **Exceptions:** Not symplectic when tracking through elements with electric fields or through `taylor` elements.

### Symp_Lie_Bmad

Similar to `symp_lie_ptc` but uses a Bmad-native routine. About 10x faster than `symp_lie_ptc` by bypassing PTC's generality. Limited to fewer element types (quadrupole, solenoid, sol_quad, wiggler).

### Taylor

Tracks using a Taylor map either explicitly defined in the lattice file (for `taylor` elements) or generated via PTC. Map generation can be slow but subsequent tracking is very fast. Non-symplectic away from the expansion point. Map order set by `parameter[taylor_order]`.

### Linear

Tracks using only the 0th-order vector plus the 1st-order 6x6 transfer matrix. Always uses zero orbit as the reference orbit (to avoid circular dependency). Cannot be used with `mat6_calc_method = tracking`. Does not affect PTC calculations.

### MAD

Uses the MAD 2nd-order transfer map. Cannot handle element misalignments or kicks. Inaccurate when particle energy deviates from reference. For testing purposes only.

### Custom

Calls user-supplied custom tracking code.

---

## Tracking Method Availability by Element Type

"D" = default, "X" = available. Runge_Kutta column includes fixed-step variants. For photon tracking, only `bmad_standard` and `custom` are available.

| Element                       | Bmad_Standard | Custom | Linear | MAD | Runge_Kutta | Symp_Lie_Bmad | Symp_Lie_PTC | Taylor | Time_Runge_Kutta |
|-------------------------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| ab_multipole, multipole       |  D  |  X  |  X  |     |     |     |  X  |  X  |     |
| ac_kicker                     |  D  |  X  |  X  |     |  X  |     |     |     |  X  |
| beambeam                      |  D  |  X  |  X  |     |     |     |     |     |     |
| bends (rbend, sbend)          |  D  |  X  |  X  |  X  |  X  |     |  X  |  X  |  X  |
| converter                     |  D  |  X  |     |     |     |     |     |     |     |
| crab_cavity                   |  D  |  X  |  X  |     |     |     |     |     |     |
| custom                        |     |  D  |  X  |     |  X  |     |     |     |  X  |
| drift                         |  D  |  X  |  X  |  X  |  X  |     |  X  |  X  |  X  |
| e_gun                         |     |  X  |     |     | X*  |     |     |     |  D  |
| ecollimator, rcollimator      |  D  |  X  |  X  |     |  X  |     |  X  |  X  |  X  |
| elseparator                   |  D  |  X  |  X  |  X  |  X  |     |  X  |  X  |  X  |
| em_field                      |     |  X  |     |     |  D  |     |  X  |  X  |  X  |
| fiducial                      |  D  |  X  |     |     |     |     |  X  |     |     |
| floor_shift                   |  D  |  X  |     |     |     |     |  X  |     |     |
| fork                          |  D  |  X  |  X  |     |     |     |     |     |     |
| gkicker                       |  D  |  X  |  X  |     |     |     |  X  |  X  |     |
| hkicker                       |  D  |  X  |  X  |     |  X  |     |  X  |  X  |  X  |
| instrument, monitor, pipe     |  D  |  X  |  X  |     |  X  |     |  X  |  X  |  X  |
| kicker                        |  D  |  X  |  X  |     |  X  |     |  X  |  X  |  X  |
| lcavity, rfcavity             |  D  |  X  |  X  |     |  X  |     |  X  |  X  |  X  |
| marker                        |  D  |  X  |  X  |     |     |     |  X  |  X  |     |
| match                         |  D  |  X  |     |     |     |     |     |  X  |     |
| octupole                      |  D  |  X  |  X  |     |  X  |     |  X  |  X  |  X  |
| patch                         |  D  |  X  |     |     | X** |     |  X  |  X  |     |
| photonic elements             |  D  |  X  |     |     |     |     |     |     |     |
| quadrupole                    |  D  |  X  |  X  |  X  |  X  |  X  |  X  |  X  |  X  |
| rf_bend                       |     |  X  |  X  |     |  X  |     |     |     |  X  |
| sad_mult                      |  D  |  X  |  X  |     |     |     |  X  |  X  |     |
| sextupole                     |  D  |  X  |  X  |  X  |  X  |     |  X  |  X  |  X  |
| solenoid                      |  D  |  X  |  X  |  X  |  X  |  X  |  X  |  X  |  X  |
| sol_quad                      |  D  |  X  |  X  |     |  X  |  X  |  X  |  X  |  X  |
| taylor                        |     |  X  |  X  |     |     |     |  X  |  D  |     |
| vkicker                       |  D  |  X  |  X  |     |  X  |     |  X  |  X  |  X  |
| wiggler (map type)            |     |  X  |  X  |     |  X  |  X  |  X  |  X  |  X  |
| wiggler (periodic type)       |  D  |  X  |  X  |     |  X  |  X  |  X  |  D  |     |

\* Only if beginning energy is non-zero.
\** Only for non-reflection patch elements.

---

## Linear Transfer Map Methods

### Auto

Selects the `mat6_calc_method` appropriate for the element's `tracking_method`:

| tracking_method          | mat6_calc_method used |
|--------------------------|----------------------|
| `bmad_standard`          | `bmad_standard`      |
| `linear`                 | `bmad_standard`      |
| `custom`                 | `custom`             |
| `mad`                    | `mad`                |
| `symp_lie_bmad`          | `symp_lie_bmad`      |
| `symp_lie_ptc`           | `symp_lie_ptc`       |
| `taylor`                 | `taylor`             |
| All Runge-Kutta types    | `tracking`           |

### Bmad_Standard (mat6)

Uses analytic formulas with paraxial approximation. Fast.

### Symp_Lie_PTC (mat6)

Symplectic integration via PTC. Accurate and symplectic but slow. Not symplectic for elements with electric fields or `taylor` elements.

### Symp_Lie_Bmad (mat6)

Symplectic Lie integration using Bmad routines. About 10x faster than `symp_lie_ptc`. Cannot generate maps above first order.

### Taylor (mat6)

Uses a Taylor map generated from PTC. Generation is slow, evaluation is fast. Non-symplectic away from expansion point. Taylor maps for `match` and `patch` elements are limited to first order. Map order set by `parameter[taylor_order]`.

### Tracking (mat6)

Tracks 6 particles around the central orbit using the element's `tracking_method` to numerically compute the Jacobian. Susceptible to inaccuracies from nonlinearities. Slow. Cannot be used with `tracking_method = linear`. The deltas used for displacing particles are set by `bmad_com%d_orb(6)`.

### MAD (mat6)

MAD 2nd-order transfer map. Cannot handle misalignments or kicks. For testing only.

### Custom (mat6)

Calls user-supplied calculation code.

Additional attributes affecting transfer matrix calculation:
- `static_linear_map` -- when `True`, prevents the linear map from being recomputed when lattice changes occur.
- `symplectify` -- when `True`, forces the transfer matrix to be symplectic.
- `taylor_map_includes_offsets` -- controls whether Taylor map generation accounts for element misalignments.

---

## mat6_calc_method Availability by Element Type

"D" = default, "X" = available. Transfer matrices are not computed for photon tracking.

| Element                       | Auto | Bmad_Standard | Custom | MAD | Static | Symp_Lie_Bmad | Symp_Lie_PTC | Taylor | Tracking |
|-------------------------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| ab_multipole, multipole       |  D  |  X  |  X  |     |  X  |     |  X  |  X  |  X  |
| ac_kicker                     |     |     |  X  |     |  X  |     |  X  |  X  |  D  |
| beambeam                      |  D  |  X  |  X  |     |  X  |     |     |     |  X  |
| bends (rbend, sbend)          |  D  |  X  |  X  |  X  |  X  |     |  X  |  X  |  X  |
| custom                        |     |     |  D  |     |  X  |     |     |     |  X  |
| drift                         |  D  |  X  |  X  |  X  |  X  |     |  X  |  X  |  X  |
| e_gun                         |     |     |  X  |     |  X  |     |     |     |  D  |
| em_field                      |     |     |  X  |     |  X  |     |  X  |  X  |  D  |
| lcavity, rfcavity             |  D  |  X  |  X  |     |  X  |     |  X  |  X  |  X  |
| quadrupole                    |  D  |  X  |  X  |  X  |  X  |  X  |  X  |  X  |  X  |
| solenoid                      |  D  |  X  |  X  |  X  |  X  |  X  |  X  |  X  |  X  |
| sol_quad                      |  D  |  X  |  X  |  X  |  X  |  X  |  X  |  X  |  X  |
| taylor                        |     |     |  X  |     |  X  |     |  X  |  D  |     |
| wiggler (map type)            |  D  |  X  |  X  |     |  X  |  X  |  X  |  X  |  X  |
| wiggler (periodic type)       |     |     |  X  |     |  X  |  X  |  X  |  D  |  X  |

(Rows for other element types follow the same pattern as the tracking method table, with most having `auto` as default and supporting `bmad_standard`, `custom`, `static`, `symp_lie_ptc`, `taylor`, and `tracking`.)

---

## Spin Tracking Methods

| Method             | Description |
|--------------------|-------------|
| `tracking`         | Default for most elements. Uses the `tracking_method` to determine how spin is tracked. With Runge-Kutta methods, spin is integrated alongside orbital coords. With `symp_lie_ptc`, PTC handles spin. Otherwise uses Romberg integration of the spin rotation matrix. |
| `symp_lie_ptc`     | Symplectic Lie integration via PTC. Symplectic but slow. |
| `magnus`           | Second-order Magnus expansion of the T-BMT equation. Fast and closely matches numerical integration in most cases. |
| `sprint`           | Uses first-order transfer spin maps. Very fast but less accurate away from zero orbit. Limited element support; ignores higher-order multipoles. |
| `custom`           | Calls user-supplied `track1_spin_custom` routine. |
| `transverse_kick`  | Assumes orbital transfer is due solely to transverse magnetic fields. Relates spin rotation to $\Delta p_x$ and $\Delta p_y$. |
| `off`              | No spin tracking; spin at exit equals spin at entrance. |

Global spin control: `bmad_com[spin_tracking_on]` determines whether spin is tracked at all.

The `spin_fringe_on` element attribute toggles whether fringe fields affect spin.

```
q: quadrupole, spin_tracking_method = symp_lie_ptc
```

### Spin Method Availability by Element Type

| Element                       | Off | Custom | Magnus | Sprint | Symp_Lie_PTC | Tracking | Transverse_Kick |
|-------------------------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| ab_multipole, multipole       |  X  |  X  |     |     |     |  D  |     |
| bends (rbend, sbend)          |  X  |  X  |  X  |  X  |  X  |  D  |     |
| drift                         |  X  |  X  |  X  |  X  |  X  |  D  |     |
| e_gun                         |  X  |  X  |     |     |     |  D  |     |
| em_field                      |  X  |  X  |     |     |     |  D  |     |
| lcavity, rfcavity             |  X  |  X  |     |     |  X  |  D  |     |
| match                         |  D  |     |     |     |     |     |  X  |
| quadrupole                    |  X  |  X  |  X  |  X  |  X  |  D  |     |
| sextupole                     |  X  |  X  |  X  |  X  |  X  |  D  |     |
| solenoid                      |  X  |  X  |  X  |  X  |  X  |  D  |     |
| sol_quad                      |  X  |  X  |     |     |  X  |  D  |  X  |

(Most other elements support `off`, `custom`, and `tracking` (default). See complete table in Bmad manual.)

---

## Step Size Control and Integration Parameters

### ds_step and num_steps

Integration methods divide elements into slices. The slice thickness is controlled by:

```
q: quadrupole, l = 0.6, ds_step = 0.1    ! 10 cm step size
sbend::*[ds_step] = 0.2                  ! Set for all sbend elements
q2: quadrupole, l = 0.6, num_steps = 6   ! Alternative: specify number of steps
```

`ds_step` and `num_steps` apply to `symp_lie_bmad`, `symp_lie_ptc`, `taylor`, and fixed-step Runge-Kutta methods. The default `ds_step` for a given element is estimated from its field strength; treat this as a rough guess.

For PTC-based methods, both `ds_step` (or `num_steps`) and `integrator_order` affect accuracy. Best practice: use a high integrator order with a small step size. For elements with longitudinally varying fields (wigglers, undulators), the step size must be small compared to the pole period length.

### Runge-Kutta Adaptive Stepping

`runge_kutta` and `time_runge_kutta` use adaptive step control independent of `ds_step`. Three `bmad_com` parameters govern the behavior:

```
bmad_com[rel_tol_adaptive_tracking]   ! Relative tolerance
bmad_com[abs_tol_adaptive_tracking]   ! Absolute tolerance
bmad_com[max_num_runge_kutta_step]    ! Max number of steps allowed
```

The error bound per step is:

```
error < abs_tol + |orbit| * rel_tol
```

Lowering tolerances improves accuracy (until round-off errors dominate) but slows tracking. Adaptive stepping is almost always faster than fixed-step tracking and is strongly recommended.

### PTC Integration Order

The `integrator_order` attribute sets the order of the integration formula for `symp_lie_ptc`:

```
integrator_order = 2, 4, 6, or 8
```

Error in an integration step scales as $dz^{n+1}$ where $n$ is the integrator order. For wigglers, order 2 is typically fastest after adjusting `ds_step` for accuracy. `symp_lie_bmad` always uses order 2 regardless of this setting. Order 8 is not implemented for all elements (falls back to 6).

---

## field_calc Parameter

Controls how EM fields are calculated for Runge-Kutta type tracking:

For most elements:
```
field_calc = bmad_standard    ! Default (except custom elements)
field_calc = custom           ! Default for custom elements
field_calc = fieldmap         ! Use field maps
```

For wigglers and undulators:
```
field_calc = planar_model     ! Default (if no field map present)
field_calc = helical_model
field_calc = custom
field_calc = fieldmap         ! Default if field map is present
```

With `bmad_standard` tracking, `field_calc` is ignored except for wigglers/undulators.

```
q1: quadrupole, l = 0.6, tracking_method = runge_kutta,
      mat6_calc_method = symp_lie_ptc, ds_step = 0.2, field_calc = fieldmap
```

---

## Relative vs Absolute Time Tracking

Controlled by `bmad_com[absolute_time_tracking]`. Affects how the RF phase is computed for `lcavity`, `rfcavity`, and `em_field` elements.

**Relative time tracking** (default): The effective time $t_{\text{eff}}$ is derived from the phase space coordinate $z$. A particle on the reference orbit always has $t_{\text{eff}} = 0$. Transfer maps are time-independent. The closed orbit is essentially independent of RF frequency, which simplifies analysis but can produce unphysical results.

**Absolute time tracking**: Uses the particle's absolute time. More physically correct -- RF cavities with non-commensurate frequencies are properly handled. Transfer maps become turn-dependent, complicating analysis.

Key considerations:
- PTC-based tracking always uses relative time, regardless of `bmad_com[absolute_time_tracking]`.
- Long-range wakefields always use absolute time (their frequencies are not commensurate with the fundamental mode).
- Do not confuse absolute time tracking with `time_runge_kutta` -- the former changes RF phase computation; the latter changes the integration variable.

```
bmad_com[absolute_time_tracking] = True
bmad_com[absolute_time_ref_shift] = True   ! Default; subtracts reference time at element entrance
```

---

## Symplectic vs Non-Symplectic Tracking

Symplecticity is typically only relevant for long-term tracking over many turns with minimal radiation. Single-pass calculations (Twiss parameters, linac tracking) generally do not benefit from symplectic tracking.

For radiating particles, the motion is inherently non-symplectic. If radiation damping times are short relative to symplectic error accumulation, `bmad_standard` is adequate. However, symplectic errors can cause artificial damping or anti-damping, biasing equilibrium beam sizes.

### symplectify Attribute

Forces the 6x6 transfer matrix to be symplectic:

```
s1: sextupole, symplectify = True, l = 0.34
s1: sextupole, symplectify, l = 0.34          ! Equivalent
```

Default is `False`. For `lcavity` elements (where reference momentum changes), symplectification is performed in a frame with constant reference momentum.

### taylor_map_includes_offsets Attribute

Controls whether Taylor maps include the effect of element misalignments (offsets, pitches, tilt). Default is `True`.

- `True`: Map must be regenerated when the element is repositioned, but tracking is faster per evaluation.
- `False`: Map is invariant under element repositioning, but each tracking call computes the offset effect.

---

## Taylor Maps

### Taylor Map Structure

A Taylor map $\mathcal{M}: \mathcal{R}^6 \rightarrow \mathcal{R}^6$ maps starting phase space coordinates to ending coordinates:

$$r_i(\text{out}) = \sum_j C_{ij} \prod_{k=1}^{6} (\delta r_k)^{e_{ijk}}$$

where $\delta \mathbf{r} = \mathbf{r}(\text{in}) - \mathbf{r}_{\text{ref}}$. The map order is set by `parameter[taylor_order]`. All Taylor maps above first order are calculated via PTC.

### Spin Taylor Maps

Spin transport is represented by a quaternion whose four components are each a Taylor series in the six orbital phase space coordinates. Total map: 10 Taylor series (6 orbital + 4 spin quaternion), each depending on the 6 orbital variables. Stern-Gerlach effects are neglected.

Spin transport procedure:
1. Evaluate the four spin Taylor series using the orbital coordinates to produce quaternion $\mathbf{q}$.
2. Normalize: $\mathbf{q} \rightarrow \mathbf{q}/|\mathbf{q}|$.
3. Rotate spin: $\mathbf{S} \rightarrow \mathbf{q} \, \mathbf{S} \, \mathbf{q}^{-1}$.

### Symplectification of Matrices

Non-symplectic matrices are corrected using Healy's method: form $\mathbf{V} = \mathbf{S}(\mathbf{I} - \mathbf{M})(\mathbf{I} + \mathbf{M})^{-1}$, symmetrize to get $\mathbf{W} = (\mathbf{V} + \mathbf{V}^T)/2$, then compute the symplectic matrix $\mathbf{F} = (\mathbf{I} + \mathbf{S}\mathbf{W})(\mathbf{I} - \mathbf{S}\mathbf{W})^{-1}$.

### Map Concatenation and Feed-Down

When concatenating two maps $M_3 = M_2(M_1)$, if both are correct to $n$th order, $M_3$ is also correct to $n$th order **only if** $M_1$ has no constant (0th-order) term. Non-zero constant terms cause lower-order errors through feed-down. Solution: use coordinates where constant terms vanish (e.g., closed orbit coordinates).

### Symplectic Integration of Maps

Symplectic integration avoids feed-down problems entirely. It uses the Hamiltonian plus an input map to produce an output map. The element is sliced (controlled by `ds_step`) and integrated step by step. Bmad supports integrator orders 2, 4, and 6. Optimal order depends on the element -- order 2 is often fastest for strongly nonlinear elements like wigglers.

---

## X-Ray / Photon Tracking

When tracking photons, only `bmad_standard` and `custom` tracking methods are available. Transfer matrices are not computed for photon tracking.

### Coherent vs Incoherent Tracking

Photons carry a transverse electric field $(E_x, E_y)$ with amplitude and phase.

**Incoherent tracking:** Phase information is not used for intensity calculations. Power per unit area:

$$S_{x,y} = \frac{\alpha_p}{N_0 \, dA} \sum_{j \in \text{hits}} E_{x,y}^2(j)$$

**Coherent tracking:** Full complex field (amplitude and phase) is used. Field at observation point:

$$E = \frac{\alpha_p}{N_0 \, dA} \sum_{j \in \text{hits}} E(j)$$

For coherent tracking, the electric field varies with propagation length (a bookkeeping convention to ensure results match Kirchhoff's integral). At diffraction plates, a Monte Carlo integration of Kirchhoff's integral is performed.

At beam-splitting junctions (e.g., Laue diffraction, partial mirrors), channel probabilities $P_i$ and field ratios $\hat{E}_i$ must satisfy $\sum P_i = 1$.

### Partially Coherent Simulations

Photons are divided into sets. Within a set, tracking is coherent (fields summed). Between sets, results are combined incoherently (intensities summed).

---

## PTC Integration

### Single-Element vs Whole-Lattice Mode

**Single-element mode:** PTC is used on a per-element basis. Non-PTC and PTC tracking methods can be mixed to optimize speed and accuracy. Flexible, but precludes PTC's analysis tools (normal form analysis, beam envelope tracking) which require the entire lattice.

**Whole-lattice mode:** A series of PTC layouts (equivalent to Bmad branches) are created from the full Bmad lattice. Enables full PTC analysis capabilities.

### PTC Tracking Parameters

```
ptc_com[exact_model]    = <Logical>   ! Default: True. Full Hamiltonian (no paraxial approx)
ptc_com[exact_misalign] = <Logical>   ! Default: True. Exact misalignment handling
```

When `exact_model = False`, the paraxial approximation is used. Important for bends with small radii. PTC always uses exact tracking for elements with electric fields (and tracking is not symplectic in this case).

Hamiltonian splitting for individual elements:

```
q2: quad, l = 0.6, k1 = 0.34, ptc_integration_type = drift_kick
```

Options:
- `drift_kick` -- quadrupolar field included in the kick between drifts.
- `matrix_kick` -- (default) quadrupolar component used for matrix tracking between kicks. Tune tends to be insensitive to number of integration steps.
- `ripken_kick` -- for benchmarking with SixTrack.

PTC does not implement `matrix_kick` for elements with electric fields; `drift_kick` is used automatically.

---

## Simulation Modules

Bmad includes modules for simulating instrumental measurement errors.

### Orbit Measurement Simulation

Relates measured position to true position through gain errors, tilt, crunch, noise, and offsets:

$$\begin{pmatrix} x \\ y \end{pmatrix}_{\text{meas}} = n_f \begin{pmatrix} r_1 \\ r_2 \end{pmatrix} + \mathbf{M}_m \left[ \begin{pmatrix} x \\ y \end{pmatrix}_{\text{true}} - \begin{pmatrix} x \\ y \end{pmatrix}_{0} \right]$$

where $n_f$ is measurement noise, $r_1, r_2$ are unit Gaussian random numbers, and $\mathbf{M}_m$ encodes gain errors ($dg_x$, $dg_y$), tilt ($\theta$), and crunch ($\psi$). Each parameter has error and calibration components (e.g., $x_0 = x_{\text{off}} - x_{\text{calib}}$).

### Dispersion Measurement Simulation

Simulated as two orbit measurements at different energies. Noise is scaled by $\sqrt{2}/(\Delta E/E)$.

### Coupling Measurement Simulation

Simulated by measuring beam oscillation at a normal mode frequency over $N_s$ turns with amplitude $A_{\text{osc}}$. Coupling is expressed through $K$ coefficients related to the $\bar{\mathbf{C}}$ coupling matrix. Measurement errors from noise scale as $n_f / (N_s \cdot A_{\text{osc}})$.

### Phase Measurement Simulation

Betatron phase measured over $N_s$ turns of oscillation. Noise contribution scales as $n_f / (N_s \cdot A_{\text{osc}})$.

---

## CSR and Space Charge Methods

Per-element switches for collective effects during beam tracking:

```
csr_method          = off | 1_dim
space_charge_method = off | slice | fft_3d | cathode_fft_3d
```

Requires `bmad_com[csr_and_space_charge_on] = True` to take effect.

Constraints:
- `1_dim` CSR cannot be used with `cathode_fft_3d` space charge.
- `cathode_fft_3d` requires `csr_method = off` and `tracking_method` set to `time_runge_kutta` or `fixed_step_time_runge_kutta`.

```
q1: quadrupole, l = 0.6, csr_method = 1_dim, space_charge_method = slice
```
