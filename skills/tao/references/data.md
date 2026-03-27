# Tao Reference: Data

> See `SKILL.md` for navigation across all Tao reference files.

## Table of Contents

- [Data Organization](#data-organization)
- [Anatomy of a Datum](#anatomy-of-a-datum)
- [Datum Values](#datum-values)
- [Evaluation Point](#evaluation-point)
- [Evaluation Ranges](#evaluation-ranges)
- [Data Source](#data-source)
- [Merit Types](#merit-types)
- [Data Types Table](#data-types-table)
- [useit_opt and useit_plot Formulas](#useit_opt-and-useit_plot-formulas)

---

## Data Organization

A Tao "datum" is a parameter associated with a lattice used in lattice correction or design. Example data includes the vertical orbit at a particular position or the horizontal emittance of a storage ring.

Data is organized in a three-level hierarchy:

- **`d2_data`** -- A top-level structure holding a set of `d1_data` structures.
- **`d1_data`** -- Holds an array of individual datums.
- **datum** -- A single data point (e.g., horizontal orbit at one BPM).

For example, a `d2_data` structure for orbit data could contain two `d1_data` structures: one for horizontal orbit (`x`) and one for vertical orbit (`y`).

### Naming Conventions

Data is referred to using the format `d2_name.d1_name`. For example, if the `d2_data` name is `orbit` and the `d1_data` name is `x`, use `orbit.x`. If there is only one `d1_data` structure, the `d2_data` name alone suffices. Period characters are not allowed in `d2_data` or `d1_data` names.

Individual datums are referenced as:

```
<d2_name>.<d1_name>[<list_of_datum_indexes>]
```

For example, `orbit.x[10]` refers to datum index 10. The starting index is user-selectable.

### Indexing and Ranges

Ranges use commas and colons:

```
orbit.x[3:6,23]       ! Datums 3, 4, 5, 6, and 23
```

### Universe Prefix

With multiple universes, use the `@` prefix:

```
[2:4,7]@orbit.x       ! orbit.x data in universes 2, 3, 4, and 7
2@orbit.x              ! orbit.x data in universe 2
orbit.x                ! orbit.x in the current default universe
```

### Component Access

Each datum has components accessed with `|`:

```
orbit.x[3:10]|meas     ! The measured data values
```

### Wildcards

A `*` denotes "all":

```
*@orbit.x              ! orbit.x data in all universes
*                      ! All data in the current default universe
orbit.x[*]|meas        ! All measured values of orbit.x
orbit.x[]|meas         ! Empty set
orbit.x|meas           ! Same as orbit.x[*]|meas
```

---

## Anatomy of a Datum

Each datum has the following components. Components marked (set by Tao) are computed by Tao and not directly user-settable. Components marked (used by extensions) are reserved for Tao extension code.

### Identification Components

- **`data_type`** -- Type of data: `orbit.x`, `beta.a`, etc. If not specified at startup, defaults to `<d2_name>.<d1_name>`.
- **`merit_type`** -- Type of constraint: `target`, `max`, `min`, etc. See Merit Types section.
- **`data_source`** -- How the datum is calculated: `lat`, `beam`, or `data`. See Data Source section.

### Element Association Components

- **`ele_name`** -- Name of the lattice element where datum is evaluated, or last element in a range. Not used for global datums like emittance.
- **`ele_start_name`** -- Starting element of a range of lattice elements.
- **`ele_ref_name`** -- Reference lattice element (fiducial point). Not to be confused with the `ref` value component.
- **`eval_point`** -- Set to `beginning`, `center`, or `end`. Determines where within the element the datum is evaluated. Ignored when using an evaluation range.
- **`s_offset`** -- Offset of the evaluation point from `eval_point`. Ignored for the reference point and when using an evaluation range.
- **`ix_bunch`** -- Bunch number to get data from (for `data_source` = `beam`).
- **`spin_axis`** -- Structure used for Spin G-matrix calculations (`spin_g_matrix` data type).

### Index Components

- **`ix_ele`** (set by Tao) -- Index of `ele` in the lattice element list.
- **`ix_branch`** (set by Tao) -- Lattice branch index for `ele`, `ref_ele`, and `start_ele`.
- **`ix_ele_start`** (set by Tao) -- Index of `ele_start` in the lattice element list.
- **`ix_ele_ref`** (set by Tao) -- Index of `ele_ref` in the lattice element list.
- **`ix_ele_merit`** (set by Tao) -- When `merit_type` is `max` or `min` over a range, set to the element where the extremum occurs.
- **`ix_d1`** (set by Tao) -- Index number in `d1_data` structure.
- **`ix_data`** (set by Tao) -- Index in the global data array.
- **`ix_dModel`** (set by Tao) -- Row number in the dModel_dVar derivative matrix.

### Value Components

- **`model`** (set by Tao) -- Datum value calculated from the model lattice.
- **`design`** (set by Tao) -- Datum value calculated from the design lattice.
- **`base`** (set by Tao) -- Datum value calculated from the base lattice.
- **`meas`** -- User-set measured datum value. When fitting, this is the measurement; when designing, the desired value.
- **`ref`** -- User-set reference datum value. Typically a measurement from a reference data set.
- **`old`** (set by Tao) -- Saved model value from a previous time. Can generally be ignored.
- **`fit`** (used by extensions) -- Not used by Tao. Available for custom code.
- **`s`** (set by Tao) -- Longitudinal s-position of the associated element.

### Merit and Optimization Components

- **`weight`** -- Weight for the merit function term.
- **`delta_merit`** (set by Tao) -- Difference used to calculate the merit function contribution.
- **`merit`** (set by Tao) -- Merit function term value: `weight * delta^2`.
- **`invalid`** -- Value used for `delta_merit` when `good_model` is False, or `good_base`/`good_design` is False when the corresponding `opt_with_base`/`opt_with_ref` global is True.
- **`error_rms`** -- Measurement error associated with measured/reference data. Used for drawing error bars.

### Logical Components

- **`exists`** (set by Tao) -- True if the datum exists. A datum may not exist if the type requires an element but `ele_name` is blank.
- **`good_model`** (set by Tao) -- True if the model value is valid (e.g., False if lattice is unstable).
- **`good_design`** (set by Tao) -- True if the design value is valid.
- **`good_base`** (set by Tao) -- True if the base value is valid.
- **`good_meas`** -- True if the `meas` value has been set.
- **`good_ref`** -- True if the `ref` value has been set.
- **`good_user`** -- User-settable flag. Controlled by `veto`, `restore`, and `use` commands.
- **`good_opt`** (used by extensions) -- Similar to `good_user` but unaffected by `veto`/`restore`/`use` commands.
- **`good_plot`** (set by Tao) -- True if datum is within the horizontal extent of a plot.
- **`useit_opt`** (set by Tao) -- True if datum is used for optimization. See formulas below.
- **`useit_plot`** (set by Tao) -- True if datum is used for plotting. See formulas below.

---

## Datum Values

A datum has six associated values:

- **`model`** -- Value calculated from the model lattice.
- **`design`** -- Value calculated from the design lattice.
- **`base`** -- Value calculated from the base lattice.
- **`meas`** -- When fitting: value from measurement. When designing: the desired target value.
- **`ref`** -- When fitting: value from a reference measurement. When designing: value from the design or base lattice (determined by `opt_with_base`). The `meas` value is always associated with the model lattice.
- **`old`** -- A saved model value from a previous point in Tao's calculations. Generally ignorable.
- **`fit`** -- Not used by Tao directly; available for custom code.

---

## Evaluation Point

When a datum has an associated lattice element, the default evaluation position is at the downstream (exit) end. This can be adjusted using `eval_point` and `s_offset`.

The `eval_point` component values:

```
beginning   ! Entrance end of lattice element
center      ! Center of lattice element
end         ! Exit end of lattice element (default)
```

The evaluation point is then shifted by `s_offset` from the `eval_point`. For the reference element, `eval_point` determines the position but `s_offset` is ignored.

Not all `data_type`s are compatible with a finite `s_offset` or `eval_point` set to `center`. See the Data Types Table for compatibility.

---

## Evaluation Ranges

To evaluate a datum over a range of elements, set `ele_start_name` (or `ix_ele_start`) along with `ele_name`. The range runs from the exit end of the start element to the exit end of the evaluation element.

Example:

```
data_type      = "beta.a"
ele_name       = "q12"
ele_start_name = "q45"
merit_type     = "max"
```

This evaluates the maximum a-mode beta function from element `q45` to element `q12`.

If a reference element is also specified, the datum value is the value at the evaluation point (or over the range) minus the value at the reference element.

Key rules:
- An evaluation range is not compatible with finite `s_offset` or `eval_point` = `center`.
- For closed geometry branches, the range wraps around the lattice end.
- An evaluation range does not make sense with `merit_type` = `target`.
- Tao evaluates at element ends only; insert markers for finer resolution.

| Element            | Name Component   | Index Component  |
|--------------------|------------------|------------------|
| Reference Element  | `ele_ref_name`   | `ix_ele_ref`     |
| Start Element      | `ele_start_name` | `ix_ele_start`   |
| Evaluation Element | `ele_name`       | `ix_ele`         |

---

## Data Source

The `data_source` component specifies the origin of the data:

- **`lat`** -- Data calculated from the lattice (everything except multiparticle tracking, including single-particle tracking). For example, emittance via radiation integrals.
- **`beam`** -- Data calculated from multiparticle beam tracking. For example, emittance from the bunch sigma matrix.
- **`data`** -- Data from another Tao datum in a data array.

Some data types restrict which `data_source` is valid. For example, `n_particle_loss` must use `beam`. See the Data Types Table for valid sources per type.

---

## Merit Types

The `merit_type` component determines how the datum contributes to the merit function:

- **`target`** -- The model value should match `meas` (or the reference value).
- **`min`** -- The model value should be above `meas`. Only contributes to merit when model < meas.
- **`max`** -- The model value should be below `meas`. Only contributes to merit when model > meas.
- **`abs_min`** -- Like `min` but applied to the absolute value.
- **`abs_max`** -- Like `max` but applied to the absolute value.
- **`average`** -- Average value over a range of elements (requires `ele_start_name`).
- **`integral`** -- Integral over a range of elements (requires `ele_start_name`).
- **`rms`** -- RMS value over a range of elements (requires `ele_start_name`).
- **`max-min`** -- Maximum minus minimum over a range (requires `ele_start_name`).

---

## Data Types Table

The `data_type` component specifies the type of data a datum represents. The `d2.d1` name used to refer to a datum is arbitrary and need not match the `data_type`. The table below lists all predefined data types, valid `data_source` values, and whether `s_offset` can be used.

| Data_Type | Description | data_source | s_offset? |
|-----------|-------------|-------------|-----------|
| `alpha.a`, `.b` | Normal-mode alpha function | lat | Yes |
| `apparent_emit.x`, `.y` | Apparent emittance | lat, beam | No |
| `beta.a`, `.b`, `.c` | Normal-mode beta function | lat, beam | Yes |
| `beta.x`, `.y`, `.z` | Projected beta function | beam | No |
| `bpm_cbar.22a`, `.12a`, `.11b`, `.12b` | Measured coupling | lat | Yes |
| `bpm_eta.x`, `.y` | Measured dispersion | lat | Yes |
| `bpm_orbit.x`, `.y` | Measured orbit | lat, beam | Yes |
| `bpm_phase.a`, `.b` | Measured betatron phase | lat | Yes |
| `bpm_k.22a`, `.12a`, `.11b`, `.12b` | Measured coupling | lat | Yes |
| `bunch_charge.live`, `.live_relative` | Charge of live particles | beam | No |
| `bunch_max.x`, `.y`, `.z`, `.px`, `.py`, `.pz` | Max relative to centroid | beam | No |
| `bunch_min.x`, `.y`, `.z`, `.px`, `.py`, `.pz` | Min relative to centroid | beam | No |
| `cmat.11`, `.12`, `.21`, `.22` | Coupling matrix elements | lat | Yes |
| `cbar.11`, `.12`, `.21`, `.22` | Normalized coupling matrix | lat | Yes |
| `chrom.a`, `.b` | Chromaticities for a ring | lat | No |
| `chrom.dbeta.a`, `.dbeta.b` | Normalized chromatic beta | lat | No |
| `chrom.deta.x`, `.deta.y` | Chromatic dispersions | lat | No |
| `chrom.detap.x`, `.detap.y` | Chromatic dispersion slopes | lat | No |
| `chrom.dphi.a`, `.dphi.b` | Chromatic betatron phase | lat | No |
| `chrom.w.a`, `.w.b` | Chromatic W-functions | lat | No |
| `chrom_ptc.a.N`, `.b.N` (N = 0, 1, ...) | Chromaticity Taylor terms | lat | No |
| `curly_h.a`, `.b` | Radiation integrals curly H function | lat | Yes |
| `damp.j_a`, `.j_b`, `.j_z` | Damping partition number | lat | No |
| `deta_ds.a`, `.b` | Normal-mode dispersion derivatives | lat | Yes |
| `deta_ds.x`, `.y` | Dispersion derivatives d(eta)/ds | lat | Yes |
| `dpx_dx`, `dpx_dy`, etc. | Bunch sigma matrix ratios | beam | No |
| `dynamic_aperture.N` (N = 1, 2, 3, ...) | Dynamic aperture | lat | No |
| `e_tot_ref` | Lattice reference energy (eV) | lat | No |
| `element_attrib.<attr_name>` | Lattice element attribute | lat | No |
| `emit.a`, `.b`, `.c` | Emittance (normal mode) | lat, beam | No |
| `emit.x`, `.y`, `.z` | Projected emittance | lat, beam | No |
| `eta.x`, `.y`, `.z` | Dispersions | lat, beam | Yes |
| `eta.a`, `.b` | Normal-mode dispersions | lat, beam | Yes |
| `etap.x`, `.y` | Momentum dispersions | lat, beam | Yes |
| `etap.a`, `.b` | Normal-mode momentum dispersions | lat, beam | Yes |
| `expression:<expression>` | User-defined arithmetic expression | lat | No |
| `floor.x`, `.y`, `.z`, `.theta`, `.phi`, `.psi` | Element global position | lat | Yes |
| `floor_actual.x`, `.y`, `.z`, `.theta`, `.phi`, `.psi` | Element misaligned global position | lat | Yes |
| `floor_orbit.x`, `.y`, `.z` | Global position of orbit | lat, beam | Yes |
| `floor_orbit.theta`, `.phi`, `.psi` | Global orientation of orbit | lat, beam | Yes |
| `gamma.a`, `.b` | Normal-mode gamma function | lat | Yes |
| `k.11b`, `.12a`, `.12b`, `.22a` | Coupling | lat | Yes |
| `momentum` | Momentum: P*c (eV) | lat | Yes |
| `momentum_compaction` | Momentum compaction factor | lat | No |
| `momentum_compaction_ptc.N` (N = 0, 1, ...) | Momentum compaction Taylor terms | lat | No |
| `n_particle_loss` | Number of particles lost | beam | No |
| `norm_apparent_emit.x`, `.y` | Normalized apparent emittance | lat, beam | No |
| `norm_emit.a`, `.b`, `.c` | Normalized beam emittance | lat, beam | No |
| `norm_emit.x`, `.y`, `.z` | Normalized projected emittance | lat, beam | No |
| `normal.<type>.i.<monomial>` | Normal form map component | lat | No |
| `normal.h.<monomial>` | Normal form driving term | lat | No |
| `null` | Data without model evaluation | lat, beam | No |
| `orbit.amp_a`, `.amp_b` | Orbit amplitude | lat | Yes |
| `orbit.norm_amp_a`, `.norm_amp_b` | Energy normalized amplitude | lat | Yes |
| `orbit.energy` | Total energy (eV) | lat, beam | Yes |
| `orbit.kinetic` | Kinetic energy (eV) | lat, beam | Yes |
| `orbit.x`, `.y`, `.z`, `.px`, `.py`, `.pz` | Phase space orbit | lat, beam | Yes |
| `periodic.tt.ijklm...` (1 <= i,j,k,... <= 6) | Periodic map Taylor terms | lat | No |
| `phase.a`, `.b` | Betatron phase | lat | Yes |
| `phase_frac.a`, `.b` | Fractional betatron phase | lat | No |
| `phase_frac_diff` | a - b mode phase difference | lat | No |
| `photon.intensity` | Photon total intensity | lat, beam | No |
| `photon.intensity_x`, `.intensity_y` | Photon intensity components | lat, beam | No |
| `photon.phase_x`, `.phase_y` | Photon phase | lat, beam | No |
| `ping_a.amp_x`, `.phase_x`, `.amp_y`, `.phase_y`, `.amp_sin_y`, `.amp_cos_y`, `.amp_sin_rel_y`, `.amp_cos_rel_y` | Pinged beam a-mode response | lat | No |
| `ping_b.amp_x`, `.phase_x`, `.amp_y`, `.phase_y`, `.amp_sin_x`, `.amp_cos_x`, `.amp_sin_rel_x`, `.amp_cos_rel_x` | Pinged beam b-mode response | lat | No |
| `r.ij` (1 <= i,j <= 6) | Term in linear transfer map | lat | Yes |
| `r56_compaction` | R56-like compaction factor | lat | No |
| `rad_int.i0`, `.i1`, `.i2`, `.i2_e4`, `.i3`, `.i3_e7`, `.i4a`, `.i4b`, `.i4z`, `.i5a`, `.i5b`, `.i5a_e6`, `.i5b_e6` | Lattice radiation integrals | lat | No |
| `rad_int1.i0`, `.i1`, `.i2`, etc. | Element radiation integrals | lat | No |
| `ref_time` | Reference time | lat, beam | Yes |
| `rel_floor.x`, `.y`, `.z`, `.theta` | Relative global floor position | lat | No |
| `s_position` | Longitudinal position constraint | lat | Yes |
| `sigma.x`, `.y`, `.z`, `.px`, `.py`, `.pz`, `.ij`, `.Lxy` | Bunch size (sigma matrix) | lat, beam | No |
| `slip_factor_ptc.N` (N = 0, 1, ...) | Slip factor Taylor terms | lat | No |
| `spin.depolarization_rate` | Spin depolarization rate | lat | No |
| `spin.polarization_rate` | Spin polarization rate | lat | No |
| `spin.polarization_limit` | Spin polarization limit | lat | No |
| `spin.x`, `.y`, `.z`, `.amp` | Particle spin | lat, beam | No |
| `spin_dn_dpz.x`, `.y`, `.z` | Spin dn/dpz components | lat | No |
| `spin_g_matrix.ij` (1 <= i <= 2, 1 <= j <= 6) | Spin G-matrix components | lat | No |
| `spin_res.a.sum`, `.a.diff`, `.b.sum`, `.b.diff`, `.c.sum`, `.c.diff` | Spin resonance strengths | lat | No |
| `spin_map_ptc.ijklmn` | Spin map Taylor terms | lat | No |
| `spin_tune` | Spin tune | lat | No |
| `spin_tune_ptc.N` (N = 0, 1, ...) | Spin tune Taylor terms | lat | No |
| `srdt.h<monomial>.{r,i,a}` | Driving terms by summation | lat | No |
| `time` | Particle time (sec) | lat, beam | Yes |
| `t.ijklm...`, `tt.ijklm...` (1 <= i,j,k,... <= 6) | Term in nth order transfer map | lat | No |
| `tune.a`, `.b`, `.z` | Tune (radians) | lat | No |
| `unstable.eigen`, `.eigen.a`, `.eigen.b`, `.eigen.c` | Maximum eigenvalue amplitude | lat | No |
| `unstable.lattice` | Positive if lattice is unstable | lat | No |
| `unstable.orbit` | Nonzero if particles lost in tracking | lat | No |
| `velocity`, `velocity.x`, `.y`, `.z` | Normalized velocity v/c | lat, beam | Yes |
| `wall.left_side`, `.right_side` | Building wall constraint | lat | No |
| `wire.<angle>` | Wire scanner at given angle | beam | No |

---

## useit_opt and useit_plot Formulas

For a datum, `useit_opt` is computed as:

```
useit_opt = exists & good_opt & good_user & good_meas &
            good_ref (if reference data is used in optimization)
```

Note: if `good_model` is False, the datum is still used for optimization but the `invalid` value is substituted for the computed model value in `delta_merit`.

For a datum, `useit_plot` is computed per-graph as:

```
useit_plot = exists & good_plot &
             (good_user | graph:draw_only_good_user_data_or_vars) &
             good_meas (if measured data is being plotted) &
             good_ref (if reference data is being plotted) &
             good_model (if model data is being plotted)
```
