# Tao Reference: Concepts and Syntax

> See SKILL.md for navigation to other Tao reference files.

## Data Model Hierarchy

### Super_universe

Everything known to Tao is held in a single `super_universe`. It contains:
- One or more **universes** (each with a lattice and associated data)
- **Variables** -- parameters that can be varied (e.g. quadrupole strengths)
- **Data** -- anything that can be measured (orbit, beta functions, etc.)
- **Plotting** -- graph/floor plan display information
- **Global Parameters** -- control parameters (random seed, optimizer choice, etc.)

Variables, plotting, and global parameters live at the super_universe level and are shared across universes.

### Universe

A `universe` contains a lattice plus associated data. Each universe holds three lattices (see below). Multiple universes enable simultaneous analysis of different machine configurations (e.g. orbit response matrix analysis with one universe per steering measurement).

### Three Lattice Types

| Lattice | Role |
|---------|------|
| **Design** | Read from the lattice file at startup. Fixed -- nothing may vary. |
| **Model** | Initially identical to design. All variable changes and corrections act on this lattice. |
| **Base** | Reference lattice for comparing model changes. Initially equals design; can be set to model or design via the `set` command. |

### Lattice Branches

A lattice can have multiple **branches** (e.g. two intersecting rings). Commands that operate on a branch use the default branch unless one is specified. Set the default with `set default branch`; view it with `show global`. Branch 0 is the initial default.

## Multiple Universes

Default universe is used when none is specified (initially 1; change with `set default universe`; view with `show global`). Syntax: `[<universe_range>]@<parameter>` -- commas separate universes, colons denote ranges, `*` = all, `-1` = current default. Brackets optional for a single universe.

```
[2:4,7]@orbit.x   ! Universes 2, 3, 4 and 7
2@orbit.x          ! Universe 2 (brackets optional)
*@orbit.x          ! All universes
```

## Tracking Types

Controlled by the `global%track_type` parameter in the initialization file.

- **Single particle** -- tracks one particle through the lattice (default)
- **Multi-bunch** -- creates a Gaussian distribution, tracks each particle including wakefields

Spin tracking is available for both modes. See the globals and beam initialization references.

## Lattice Calculation Cycle

After every Tao command, these seven steps execute:

1. Re-determine data and variables used by the optimizer (affected by `use`, `veto`, `restore`).
2. If lattice changed: recalculate model lattice for all universes (orbit, transfer matrices, Twiss parameters, all data types).
3. Recalculate model data from orbit, matrices, Twiss, beam info, and global parameters. Custom data calculated before standard types.
4. Run user post-processing hook (`tao_hook_post_process_data`).
5. Compute merit function contributions from variables and data.
6. Transfer data/variable values to plotting structures.
7. Regenerate the plot window.

Recalculation can be suppressed with `set global lattice_calc_on` or `set universe` when it is slow.

## Command Line Syntax

- Commands are **case sensitive** (Bmad element names are case insensitive).
- `;` separates multiple commands on one line. `!` begins a comment. `&` at end of line continues to next line. Max line length: 1000 characters.

```
set default uni = 2; show global  ! Two commands and a comment
set default &    ! Continue to next line
uni = 2
```

## Element Specification

Elements are specified by **name** or **index**. Prefix with `<universe>@` for universe and `<branch>>>` for branch.

```
Q3##2      ! 2nd element named Q3 in branch 0, default universe
134        ! Element index 134, branch 0, default universe
1>>13      ! Index 13, branch 1, default universe
2@1>>TZ    ! Element TZ, branch 1, universe 2
B37        ! Element B37, default universe
0@B37      ! Same as above
```

Element names are **not** case sensitive.

## Element List Format

A comma-separated list of items. Each item is one of:

| Item Type | Example |
|-----------|---------|
| Single element | `1>>Q10W` |
| Name with wildcards | `5@q*` |
| Range `<ele1>:<ele2>` | `b23w:67` |
| `class::name` | `sbend::b*` |

Wildcards: `*` matches any number of characters; `%` matches exactly one. Example list: `23, 45:74, quad::q*`. Ranges include both endpoints; optional class prefix filters: `quad::sex10w:sex20w`. `class::name` selects by element type and name: `4@quad::q*`.

## Arithmetic Expressions

### Operators

`+` (add), `-` (subtract), `*` (multiply), `/` (divide), `^` (exponentiate)

### Intrinsic Functions

| Function | Description |
|----------|-------------|
| `sqrt(x)` | Square root |
| `log(x)` | Logarithm |
| `exp(x)` | Exponential |
| `sin(x)`, `cos(x)` | Sine, cosine |
| `tan(x)`, `cot(x)` | Tangent, cotangent |
| `asin(x)`, `acos(x)` | Arc sine, arc cosine |
| `atan(y)`, `atan2(y,x)` | Arc tangent |
| `abs(x)` | Absolute value |
| `factorial(x)` | Factorial |
| `ran()` | Random number in [0,1] |
| `ran_gauss()` | Gaussian random, unit RMS |
| `ran_gauss(sig_cut)` | Gaussian random, truncated at sig_cut |
| `int(x)` | Nearest integer toward zero |
| `nint(x)` | Nearest integer |
| `floor(x)` | Nearest integer <= x |
| `ceiling(x)` | Nearest integer >= x |
| `modulo(a,p)` | `a - floor(a/p)*p`, result in [0,p] |
| `average(arr)` | Array average |
| `rms(arr)` | Array RMS |
| `sum(arr)` | Array sum |
| `min(arr)` | Array minimum |
| `max(arr)` | Array maximum |
| `mass_of(A)` | Mass of particle species A |
| `charge_of(A)` | Charge of species A (elementary units) |
| `anomalous_moment_of(A)` | Anomalous magnetic moment |
| `species(A)` | Integer species ID |

Array operations follow standard rules: scalars broadcast, same-length arrays operate element-wise. Aggregate functions (`sum`, `min`, etc.) take arrays in brackets: `min([a, b, c])`.

## Token Types

### `data::` -- Data Parameters

```
{[<universe(s)>]@}data::<d2.d1_name>[<index_list>]|<component>
```

```
2@data::orbit.x[4]         ! Fourth orbit.x datum, universe 2
data::orbit.x[4,7:9]|meas  ! Measured values of datums 4, 7, 8, 9
*@data::*                   ! All data, all universes
```

Data must be defined at startup in the initialization file. The `data::` prefix may be omitted in context (e.g. `set data`). Computed components (e.g. `model`) are read-only; user-set components (e.g. `meas`, `ref`) are writable.

### `var::` -- Variable Parameters

```
var::<v1_name>[<index_list>]|<component>
```
```
var::*                     ! All variables
var::quad_k1[*]|design     ! All design values of quad_k1
var::quad_k1|model         ! Same as quad_k1[*]|model
```

Variables must be defined at startup. `var::` prefix omittable in context. Computed components (e.g. `design`) are read-only.

### `lat::` -- Lattice Parameters

```
{[<universe(s)>]@}lat::<eval_param>[{<ref_ele>&}<element_list>{-><s_offset>}]{|<component>}
```

Unlike `data::`, lattice parameters are computed from the lattice and do not require initialization. The `<s_offset>` can be an expression where unqualified parameters refer to the containing element.

```
3@lat::orbit.x[34:37]            ! Orbit array at elements 34-37, universe 3
3@lat::orbit.x[q10w->-L/2]|model ! Orbit at half-length before exit of q10w
lat::r.56[q0&qa:qb]              ! r(5,6) from q0 to each element in qa:qb range
```

Note: `lat::orbit.x[10]` = lattice element index 10; `data::orbit.x[10]` = 10th datum in the data array (may differ).

### `beam::` -- Beam Parameters

```
{[<universe(s)>]@}beam::<eval_param>[{<ref_ele>&}<element_list>]{|<component>}
```

Only available when beam tracking is on. Examples: `2@beam::sigma.x[q10w]`, `beam::n_particle_loss[2&56]`.

### `ele::` and `ele_mid::` -- Element Parameters

```
{<universe(s)>@}ele::<element_list>[<parameter>]{|<component>}
{<universe(s)>@}ele_mid::<element_list>[<parameter>]{|<component>}
```

`ele::` evaluates at the element exit end; `ele_mid::` evaluates at the element center. For non-varying parameters (e.g. `k2`), use `ele::`.

```
3@ele_mid::34[orbit_x]     ! Orbit at middle of element 34, universe 3
ele::sex01w[k2]            ! Sextupole strength of sex01w
ele::Q01W[is_on]|model     ! On/off status of Q01W
```

Logical parameters convert to `1` (True) or `0` (False) when used in numeric expressions.

## Tao Datum vs Bmad Element Parameter Names

| Tao Datum | Bmad Element Parameter |
|-----------|----------------------|
| `alpha.a`, `alpha.b` | `alpha_a`, `alpha_b` |
| `beta.a`, `beta.b` | `beta_a`, `beta_b` |
| `cmat.11`, etc. | `cmat_11`, etc. |
| `e_tot` | `e_tot` |
| `eta.a`, `eta.b` | `eta_a`, `eta_b` |
| `eta.x`, `eta.y` | `eta_x`, `eta_y` |
| `etap.a`, `etap.b` | `etap_a`, `etap_b` |
| `etap.x`, `etap.y` | `etap_x`, `etap_y` |
| `floor.x`, `floor.y`, `floor.z` | `x_position`, `y_position`, `z_position` |
| `floor.theta`, `floor.phi`, `floor.psi` | `theta_position`, `phi_position`, `psi_position` |
| `gamma.a`, `gamma.b` | `gamma_a`, `gamma_b` |
| `phase.a`, `phase.b` | `phi_a`, `phi_b` |
| `orbit.x`, `orbit.y`, `orbit.z` | `x`, `y`, `z` |
| `orbit.px`, `orbit.py`, `orbit.pz` | `px`, `py`, `pz` |
| `spin.x`, `spin.y`, `spin.z` | `spin_x`, `spin_y`, `spin_z` |
| `spin.amp`, `spin.theta`, `spin.phi` | `spinor_polarization`, `spinor_theta`, `spinor_phi` |

## Format Descriptors

Tao uses Fortran-style format descriptors (case insensitive):

| Form | Output Type |
|------|-------------|
| `Aw` | String |
| `Fw.d` | Real, fixed point (no exponent) |
| `nPFw.d` | Real, fixed point with decimal shifted `n` places |
| `ESw.d` | Real, floating point (with exponent) |
| `Lw` | Logical |
| `Iw` | Integer |
| `Iw.r` | Integer, zero-padded to width `r` |
| `wX` | Whitespace (`w` spaces) |
| `Tc` | Tab to column `c` |

`w` = field width; `d` = digits after decimal. `0` for `w` auto-fits (avoid in tables). Comma-delimited lists for multiple quantities: `I4, A`. Multiplier prefixes: `3A` = `A, A, A`. Examples: `F7.2` on 76.1234 = `"  76.12"`, `ES9.2` = `" 7.61E+01"`, `I4.3` on 34 = `" 034"`.
