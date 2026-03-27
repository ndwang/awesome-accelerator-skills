# Tao Reference: Optimization and Wave Analysis

## Optimization

### Overview

"Optimization" is the process of varying `model` lattice parameters so that a given set of
properties are as close to a given set of "desired" values as possible. Optimization problems
generally fall into two categories:

- **Lattice correction** -- Matching the `model` lattice to actual measured data. For example,
  orbit flattening involves varying steerings in the `model` lattice so that the calculated orbit
  matches the measured orbit. The steering strengths can then be used to calculate what changes
  are needed to correct the orbit in the actual machine.

- **Lattice design** -- Varying lattice parameters to achieve some set of ideal properties. For
  example, varying sextupole magnet strengths to maximize dynamic aperture.

Optimization involves "data" (parameters to be optimized) and "variables" (what is varied).
Any lattice parameters can be used as long as varying the variables will affect the data.

### Merit Function

The merit function M in Tao is:

    M = sum_i w_i * [delta_D_i]^2 + sum_j w_j * [delta_V_j]^2

The first term sums over data and the second term sums over variables. The `w_i` and `w_j` are
user-specified weights stored in the `weight` component of a datum or variable. The value of
`delta_D` or `delta_V` is stored in the `delta_merit` component. The contribution to the merit
function (`[delta_D]^2` or `[delta_V]^2`) is stored in the `merit` component.

### Negative Weights for Maximization

To maximize a datum or variable value (for example, maximizing dynamic aperture), set the weight
`w` to a negative value. The contribution to the merit function will then be negative. Note: the
`lmdif` optimizer will not function correctly if there are negative weights.

### Calculation of delta_D for Data

How `delta_D` is calculated depends on the datum's `merit_type` setting:

```
"target"                       ! Default
"average"                      ! Uses evaluation range
"integral"                     ! Uses evaluation range
"rms"                          ! Uses evaluation range
"min", "max"
"abs_min", "abs_max"
"max-min"                      ! Uses evaluation range
```

An evaluation range covers the region from the element identified by `ele_start_name` to the
`ele_name` element. Data types without an associated evaluation element (such as emittance)
cannot use merit types that require an evaluation range.

#### Merit Type Descriptions

- **target** -- An evaluation range is not permitted. The value is simply the `data_type` value
  at the evaluation element (minus any reference element value).

- **average** -- The mean of the `data_type` over the evaluation region (integral normalized by
  length). Evaluated at element ends assuming linear variation.

- **integral** -- The integral of the `data_type` over the evaluation region. Evaluated at
  element ends assuming linear variation.

- **min / max** -- The minimum or maximum value of the `data_type` over the evaluation region.

- **abs_min / abs_max** -- The minimum or maximum of the absolute value of the `data_type` over
  the evaluation region.

- **max-min** -- The maximum minus the minimum value over the evaluation region.

- **rms** -- The RMS of the `data_type` over the evaluation region. Evaluated at element ends
  assuming linear variation.

#### Composite Value Expression

After `model`, `base`, and `design` values are calculated, they are combined with user-set
`meas` and `ref` values into a "composite" value. The formula depends on two global logicals:

| `opt_with_ref` | `opt_with_base` | Composite Value Expression          |
|-----------------|-----------------|-------------------------------------|
| F               | F               | model - meas                        |
| F               | T               | model - meas - base                 |
| T               | F               | (model - meas) - (design - ref)     |
| T               | T               | (model - meas) - (base - ref)       |

After the composite value is calculated, `delta_D` equals the composite value except for
`min`/`abs_min` and `max`/`abs_max` merit types:

- For `min` and `abs_min`: `delta_D = 0` if composite > 0, otherwise `delta_D = composite`.
  The datum only contributes when composite is negative.

- For `max` and `abs_max`: `delta_D = 0` if composite < 0, otherwise `delta_D = composite`.
  The datum only contributes when composite is positive.

### Calculation of delta_V for Variables

The `delta_V` terms serve to keep variables within limits or guide the optimization towards a
target value. The variable's `merit_type` can be:

```
"limit"     ! Default
"target"
```

**limit** -- `delta_V` is determined by `high_lim` and `low_lim` components:

    delta_V = model - high_lim    if model > high_lim
    delta_V = model - low_lim     if model < low_lim
    delta_V = 0                   otherwise

Default limits are +/-10^30. When `global%var_limits_on` is True and the model value exceeds
a limit, Tao sets the model value to the nearest limit and sets `good_user` to False.

**target** -- The formula for `delta_V` uses the same composite value expressions as for data
(see the table above), where `model`, `base`, and `design` are variable values from the
respective lattices.

### Unstable Data Types

When it is not possible to calculate `delta_merit` (for example, when the lattice is unstable),
the value is set equal to the datum's `invalid` component. Additionally, these data types can
drive optimization away from instability:

```
unstable.eigen
unstable.eigen.a, .b, .c
unstable.lattice
unstable.orbit
```

### Available Optimizers

**lm** -- Based on the Levenberg-Marquardt algorithm. Computes the local derivative matrix of
dData/dVariable and takes steps accordingly. The derivative matrix is recalculated each loop by
default (controlled by `global%derivative_recalc`). Variable `step` sizes must be chosen large
enough to avoid round-off errors but small enough to avoid nonlinearity effects. Only finds
local minima. Prints `a_lambda` (damping factor) as a convergence indicator -- small values
(much less than 1) indicate good agreement, large values indicate a mismatch.

**lmdif** -- Like `lm` but builds derivative information by taking small steps over the first
N cycles (where N is the number of variables), so no `step` size needs to be set. The number
of cycles must be greater than the number of variables. Only finds local minima.

**geodesic_lm** -- A variant of the Levenberg-Marquardt method that uses the derivative matrix.
Like `lm` and `svd`, requires appropriate variable `step` sizes.

**de** (Differential Evolution) -- A global optimizer. Slower at finding local minima but
explores broader variable space. The `step` size controls exploration range: the actual step
used is `step * global%de_lm_step_ratio`. The population size is:

```
population = number_of_variables * global%de_var_to_population_factor
```

A good strategy is to alternate between `de` and a local optimizer (`lm` or `lmdif`).

**svd** (Singular Value Decomposition) -- Applies SVD to the derivative matrix in one step per
loop; `global%n_opti_cycles` is ignored. If the merit function increases, variables revert to
original values (when `global%svd_retreat_on_merit_increase` is True). The
`global%svd_cutoff` parameter controls the eigenvalue singularity threshold.

### Key Optimizer Parameters

- `global%n_opti_cycles` -- Number of cycles per loop.
- `global%n_opti_loops` -- Number of loops before automatic stop.
- `global%optimizer` -- Default optimizer to use.
- `global%derivative_recalc` -- Whether to recalculate the derivative matrix each loop.
- `global%de_lm_step_ratio` -- Scale factor for DE step size relative to variable `step`.
- `global%de_var_to_population_factor` -- DE population multiplier.
- `global%var_limits_on` -- Enforce variable limits during optimization.
- `global%only_limit_opt_vars` -- Only apply limits to variables the optimizer is varying.
- `global%optimizer_var_limit_warn` -- Print warnings when variables exceed limits.
- `global%optimizer_allow_user_abort` -- Allow stopping with the period key.
- `global%svd_cutoff` -- SVD eigenvalue singularity cutoff.
- `global%svd_retreat_on_merit_increase` -- Revert SVD step if merit increases.

Example of adjusting parameters:

```
set global n_opti_loops = 30
set global n_opti_cycles = 50
```

### Key Show Commands for Optimization

```
show constraints      ! List of constraints
show data             ! Show data info
show derivative       ! Show derivative info
show merit            ! Top contributors to the merit function
show optimizer        ! Optimizer parameters
show variable         ! Show variable info
```

Use `show merit -derivative` to see which variables have the largest dMerit/dVariable values.
Use `change variable` to verify that actual derivatives match computed derivatives.

---

## Wave Analysis

### Purpose

A wave analysis is a method for finding isolated "kick errors" in a machine by analyzing
measurement data. It works on difference quantities -- for example, the difference between
measurement and theory, or between two measurements. Orbit and vertical dispersion are
exceptions since they can be analyzed directly (the difference from a perfectly flat orbit).

The success of the wave analysis depends on whether there are regions of sufficient size on both
sides of the kick that are kick-error-free -- that is, whether the kick error is "isolated."

### Supported Measurement and Error Types

| Measurement Type              | Error Type              |
|-------------------------------|-------------------------|
| Orbit                         | Steering errors         |
| Betatron phase differences    | Quadrupolar errors      |
| Beta function differences     | Quadrupolar errors      |
| Coupling                      | Skew quadrupolar errors |
| Dispersion differences        | Sextupole errors        |

### Supported Data Types

The wave analysis can be performed on the following data types:

```
orbit.x, orbit.y
beta.a,  beta.b
phase.a, phase.b
eta.x, eta.y
cbar.11, cbar.12, cbar.21      ! Analysis not possible for cbar.21
ping_a.amp_x, ping_a.phase_x
ping_a.sin_y, ping_a.cos_y
ping_b.amp_y, ping_b.phase_y
ping_b.sin_x, ping_b.cos_x
```

The curve to be analyzed must be visible. Any combination of data components may be used:
"meas", "meas-ref", "model", etc.

For circular machines, data is wrapped past the end of the lattice for another half turn to
allow analysis of kicks near the lattice boundaries.

### Three-Step Process

Performing a wave analysis in Tao is a three-step process:

```
1) Plot the data to be analyzed.
2) Use the wave command to select the data.
3) Use the set wave command to vary the fit regions.
```

The accuracy of the wave analysis depends on the accuracy of the beta function and phase
advances in the baseline lattice. Tao uses the `model` lattice for the baseline. One strategy
to improve accuracy is to first fit the `model` lattice using an orbit response matrix (ORM)
analysis or fits to beta or phase measurements.

Two regions (A and B) are chosen on either side of the suspected kick. For each region, the
data is fit using a functional form that assumes no kick errors within the region. By comparing
the fits from the two regions, the location and amplitude of the kick can be calculated.

### Key Wave Commands

- **wave** -- Sets which plotted data curve is used for the wave analysis.
- **set wave** -- Sets the A and B region locations (index ranges).
- **show wave** -- Prints analysis results.

Example `show wave` output:

```
ix_a:  35  45
ix_b:  55  70
A Region Sigma_Fit/Amp_Fit:     0.018
B Region Sigma_Fit/Amp_Fit:     0.015
Sigma_Kick/Kick:    0.013
Sigma_phi:          0.019
Chi_C:              0.037 [Figure of Merit]

Normalized Kick = k * l * beta [dimensionless]
   where k = quadrupole gradient [rad/m^2].
After Dat#     Norm_K       phi
       46      0.0705    30.431
       49      0.0705    33.573
       53      0.0705    36.715
```

The Sigma_Fit/Amp_Fit values measure how well the data is fit in each region (0 = perfect fit,
1 = poor fit). The output also shows the predicted kick locations, normalized kick amplitudes,
and betatron phase at each putative kick location.
