# PyTao API Reference

Condensed reference for the pytao Python package (v1.0.0).
Full docs: https://bmad-sim.github.io/pytao/

## Table of Contents

1. [Installation](#installation)
2. [Tao Class — Initialization](#tao-class)
3. [Core Command Methods](#core-command-methods)
4. [Element Query Methods (low-level)](#element-query-methods)
5. [Lattice Query Methods](#lattice-query-methods)
6. [Data and Variable Methods](#data-and-variable-methods)
7. [Beam and Bunch Methods](#beam-and-bunch-methods)
8. [Plotting](#plotting)
9. [Pydantic Data Models (pytao.model)](#pydantic-data-models)
10. [SubprocessTao](#subprocesstao)
11. [Tao Command Quick Reference](#tao-commands)

---

## Installation

```bash
# Preferred (includes Bmad/Tao shared library):
conda install -c conda-forge pytao

# Alternative (requires pre-installed Bmad >= 20260317 with shared libs):
pip install pytao
```

Requires Python 3.10+ and Bmad compiled with `ACC_ENABLE_SHARED="Y"`.
Depends on `ormsgpack` and `orjson` for model serialization.

---

## Tao Class

```python
from pytao import Tao

tao = Tao(
    # --- Primary initialization ---
    init_file="tao.init",          # Tao init file (str or Path)
    lattice_file="lattice.bmad",   # Bmad lattice file (str or Path)
    init="<raw init string>",      # Raw init string (parsed into individual attributes)

    # --- Plotting ---
    plot="tao",     # "tao" (default), "mpl", "bokeh", True (auto-select), False
    noplot=False,   # Disable all plotting

    # --- Common options ---
    beam_file=None,                # File with tao_beam_init namelist
    beam_init_position_file=None,  # File with initial particle positions
    command="",                    # Commands to run after startup
    data_file=None,                # Data definitions for plotting/optimization
    var_file=None,                 # Variable definitions
    startup_file=None,             # Post-init command file
    plot_file=None,                # Plotting init file

    # --- Behavior flags ---
    noinit=False,        # Skip init file
    nostartup=False,     # Skip startup command file
    no_rad_int=False,    # Skip radiation integrals
    rf_on=False,         # RF cavities on (default is on)
    reverse=False,       # Reverse lattice element order
    debug=False,         # Debug mode
    quiet=False,         # Suppress output (can break pytao — avoid)
    symbol_import=False, # Import symbols from lattice files
    external_plotting=False,
    disable_smooth_line_calc=False,
    log_startup=False,
    no_stopping=False,

    # --- Other ---
    building_wall_file=None,
    geometry="",               # "WxH" or (width, height) tuple
    hook_init_file=None,
    prompt_color="",
    slice_lattice="",
    start_branch_at="",
    so_lib="",                 # Path to libtao.so (auto-detected; or set PYTAO_LIB_PATH)
)
```

### Key Attributes
- `tao.init_output` — list of strings captured during initialization
- `tao.init_settings` — `TaoStartup` instance with parsed init parameters
- `tao.plot_backend_name` — current plotting backend name, or None for Tao-native
- `tao.matplotlib` — Matplotlib graph manager (property)
- `tao.bokeh` — Bokeh graph manager (property)
- `tao.plot_manager` — currently configured plot manager (property)

---

## Core Command Methods

### tao.cmd(command, raises=True) → list[str]
Sends a single Tao command. Returns output as a list of strings.
```python
result = tao.cmd("show lat 1:10")
tao.cmd("set ele Q1 k1 = 0.5")
```

### tao.cmds(cmds, suppress_lattice_calc=True, suppress_plotting=True, raises=True) → list
Sends multiple commands. Suppresses lattice recalculation between them by default.
```python
results = tao.cmds(["set ele Q1 k1 = 0.5", "set ele Q2 k1 = -0.3"])
```

### tao.cmd_real(command) → float
### tao.cmd_integer(command) → int

### tao.evaluate(expression) → numpy array
Evaluates a Tao expression.
```python
val = tao.evaluate("data::orbit.x[1]|model")
```

---

## Element Query Methods

All accept element identifiers: name (`"Q1"`), index (`5`), or qualified
string (`"1>>0>>5"` = universe>>branch>>index).

### tao.ele_head(ele_id, ...) → dict
Returns `name`, `key`, `s`, `ix_ele`, `ix_branch`, `ix_uni`, etc.

### tao.ele_gen_attribs(ele_id, ...) → dict
Returns general attributes (content varies by element type).

### tao.ele_twiss(ele_id, ...) → dict
Returns Twiss parameters:
`beta_a`, `alpha_a`, `gamma_a`, `phi_a`, `eta_a`, `etap_a`,
`beta_b`, `alpha_b`, `gamma_b`, `phi_b`, `eta_b`, `etap_b`, `sigma_a`, `sigma_b`, etc.

### tao.ele_orbit(ele_id, ...) → dict
Returns `x`, `px`, `y`, `py`, `z`, `pz`, `t`, `p0c`, `e_field`, `phase`, etc.

### tao.ele_mat6(ele_id, ...) → dict
Returns `mat6` (6×6 numpy array) and `vec0` (6-element array).

### tao.ele_floor(ele_id, ...) → dict
Returns floor coordinates: `x`, `y`, `z`, `theta`, `phi`, `psi`.

### tao.ele_multipoles(ele_id, ...) → dict
### tao.ele_param(ele_id, param, ...) → value
### tao.ele_methods(ele_id, ...) → dict
### tao.ele_lord_slave(ele_id, ...) → dict
### tao.ele_control_var(ele_id, ...) → dict
### tao.ele_wake(ele_id, ...) → dict
### tao.ele_wall3d(ele_id, ...) → dict
### tao.ele_chamber_wall(ele_id, ...) → dict
### tao.ele_photon(ele_id, ...) → dict
### tao.ele_spin_taylor(ele_id, ...) → dict
### tao.ele_taylor(ele_id, ...) → dict
### tao.ele_ac_kicker(ele_id, ...) → dict
### tao.ele_cartesian_map(ele_id, ...) → dict
### tao.ele_cylindrical_map(ele_id, ...) → dict
### tao.ele_grid_field(ele_id, ...) → dict
### tao.ele_elec_multipoles(ele_id, ...) → dict

---

## Lattice Query Methods

### tao.lat_list(ele_id, who, ix_uni="1", ix_branch="0", which="model") → numpy array
The workhorse for extracting arrays of values across the lattice.
```python
s     = tao.lat_list("*", who="ele.s")
beta  = tao.lat_list("*", who="ele.a.beta")
eta_x = tao.lat_list("*", who="ele.x.eta")
k1    = tao.lat_list("Quad::*", who="ele.k1")
```

Common `who` values: `ele.s`, `ele.l`, `ele.a.beta`, `ele.b.beta`, `ele.a.alpha`,
`ele.b.alpha`, `ele.a.phi`, `ele.b.phi`, `ele.x.eta`, `ele.y.eta`,
`ele.x.orbit`, `ele.y.orbit`, `ele.k1`, `ele.k2`, `ele.e_tot`.

### tao.lat_ele_list(ix_uni="1", ix_branch="0") → list[str]
Returns all element names in a branch.

### tao.lat_branch_list(ix_uni="1") → list
### tao.lat_header(ix_uni="1", ix_branch="0") → dict
### tao.lat_param_units(param_name) → str

---

## Data and Variable Methods

### tao.data_d2_array() → list
### tao.data_d1_array(d2_name) → list
### tao.data_d_array(d1_name, d2_name) → list
### tao.data_parameter(d2_datum, parameter)
### tao.data_set_design_value()
### tao.data_d2_create(d2_name, n_d1, d1_names)
### tao.data_d2_destroy(d2_name)
### tao.datum_create(datum_name, ...)
### tao.datum_has_ele(datum_name) → bool
### tao.var(v1_name) → dict
### tao.var_v1_array(v1_name) → list
### tao.var_general() → dict
### tao.derivative() → array
### tao.merit() → float
### tao.constraints() → dict

---

## Beam and Bunch Methods

### tao.beam() → dict
Returns beam configuration.

### tao.beam_init() → dict
Returns beam initialization parameters.

### tao.track_beam(start=None, end=None)
Tracks the beam through the lattice, displaying a progress bar. Accepts optional
start/end element names to track a sub-range.

### tao.bunch_params(ele_id, which="model", ix_bunch=1) → dict
Returns bunch statistics: `x_ave`, `px_ave`, `sigma_x`, `emit_a`, `norm_emit_a`,
`species`, etc.

### tao.bunch1(ele_id, coordinate, which="model", ix_bunch=1) → numpy array
Returns a numpy array of single-coordinate particle data.
Available coordinates: `x`, `px`, `y`, `py`, `z`, `pz`, `s`, `t`, `charge`,
`p0c`, `state`, `ix_ele`.

### tao.bunch_data(ele_id, which="model", ix_bunch=1) → dict
Returns particle data in openPMD-beamphysics format with momenta in eV/c:
`x`, `px`, `y`, `py`, `t`, `pz`, `status`, `weight`, `z`, `species`.

### tao.particles(ele_id, ...) → ParticleGroup
Returns an openPMD-beamphysics `ParticleGroup` directly (requires `pmd_beamphysics`).
```python
P = tao.particles("end")
P.plot("x", "px")
```

### tao.bunch_comb(ele_id, ...) → dict

---

## Plotting

### Initialization
```python
tao = Tao(init_file="tao.init", plot="mpl")    # Matplotlib
tao = Tao(init_file="tao.init", plot="bokeh")   # Bokeh (best for Jupyter)
tao = Tao(init_file="tao.init", plot=True)       # Auto-select best available
```

### tao.plot(template_name)
Renders a Tao plot template using the active backend.
```python
tao.plot("beta")        # Beta functions
tao.plot("orbit")       # Orbit
tao.plot("eta")         # Dispersion
tao.plot("floor_plan")  # Floor plan
```

### tao.plot_field(ele_id, ...)
### tao.plot_page() → dict
### tao.update_plot_shapes()

### Custom matplotlib plotting
```python
import matplotlib.pyplot as plt
s = tao.lat_list("*", who="ele.s")
beta_a = tao.lat_list("*", who="ele.a.beta")
beta_b = tao.lat_list("*", who="ele.b.beta")
fig, ax = plt.subplots()
ax.plot(s, beta_a, label=r"$\beta_a$")
ax.plot(s, beta_b, label=r"$\beta_b$")
ax.set_xlabel("s [m]"); ax.set_ylabel(r"$\beta$ [m]"); ax.legend()
```

### Handling startup plotting conflicts
If a tao.init file contains plotting commands that conflict with PyTao's backends:
```python
from pytao import Tao, filter_tao_messages_context
with filter_tao_messages_context(functions=["tao_find_plots"]):
    tao = Tao(init_file="tao.init", plot="mpl")
```

---

## Pydantic Data Models (`pytao.model`)

PyTao provides Pydantic v2 models representing the live state of Tao. Models are
auto-generated from Bmad/Tao structure definitions. All support `.write()` /
`.from_file()` for JSON, `.json.gz`, msgpack (fastest, via `ormsgpack`), and YAML.

### TaoConfig
Captures the complete session state: startup parameters, BmadCom, SpaceChargeCom,
BeamInit, Beam, TaoGlobal, and per-element overrides.

```python
config = tao.get_config()
config.beam_init.a_emit = 1e-8
config.set(tao)                    # apply all settings
config.set(tao, only_changed=True) # apply only what differs from current state

# Generate commands without applying:
cmds = config.get_set_commands(tao=tao)  # only diffs
cmds = config.set_commands               # all

# Serialize:
config.write("state.msgpack")
config2 = TaoConfig.from_file("state.msgpack")

# Archive to a reproducible bash script:
config.write_bash_loader_script("dir/", tao=tao, prefix="run")
```

### Settings Sub-Models

Each sub-model can be used independently. All provide `from_tao()`, `set()`,
`get_set_commands()`, and `set_context()` (a context manager for temporary changes
that auto-restores settings on exit).

**BmadCom** — Bmad common settings
```python
from pytao.model import BmadCom
com = BmadCom.from_tao(tao)
```

**SpaceChargeCom** — space charge settings
```python
from pytao.model import SpaceChargeCom
sc = SpaceChargeCom.from_tao(tao)
```

**BeamInit** — beam initialization parameters
```python
from pytao.model import BeamInit
bi = BeamInit.from_tao(tao)
bi.a_emit = 1e-6
with bi.set_context(tao):
    tao.track_beam()   # runs with modified emittance
# original settings restored here
```

**Beam** — beam tracking parameters
```python
from pytao.model import Beam
beam = Beam.from_tao(tao)
```

**TaoGlobal** — Tao global settings
```python
from pytao.model import TaoGlobal
g = TaoGlobal.from_tao(tao)
```

### Element (high-level model)

`tao.ele()` returns an `Element` object aggregating all data for one lattice element.
Data fields load on demand, controlled by boolean flags and a `DEFAULTS` set.

```python
ele = tao.ele("Q00W")
ele.head.name             # element name
ele.head.key              # element type (e.g., "Quadrupole")
ele.twiss.beta_a          # horizontal beta function
ele.twiss.alpha_a         # horizontal alpha
ele.orbit.x               # horizontal orbit
ele.mat6.mat6             # 6×6 transfer matrix (numpy array)
ele.mat6.vec0             # 0th order vector
ele.attrs["k1"].data      # general attribute value (requires .data accessor)
ele.floor.end.actual.x    # floor x-coordinate (hierarchy: ref/entrance/center/end × actual)
ele.multipoles            # multipole data
ele.lord_slave            # lord/slave relationships
ele.control_vars          # control variables dict
ele.symplectic_error      # symplectic error (property)
ele.id                    # fully-qualified ElementID
```

Controlling what loads:
```python
ele = tao.ele("Q1", orbit=False, mat6=False)         # skip specific fields
ele = tao.ele("Q1", defaults=False, twiss=True)       # minimal: only twiss
ele = tao.ele("Q1", comb=True)                        # include comb (off by default)
```

### tao.eles(match_str, ...) → list[Element]
Queries multiple elements using Tao's element matching syntax.
```python
quads = tao.eles("Quad::*")       # all quadrupoles
range_eles = tao.eles("1:20")     # elements 1 through 20
all_eles = tao.eles("*")          # everything
```

### Lattice (high-level model)
A collection of `Element` objects with lookup dictionaries.
```python
from pytao.model import Lattice
lattice = Lattice.from_tao_unique(tao, ix_uni="1", ix_branch="0")
# Also: from_tao_tracking, from_tao_eles, from_file

lattice.by_element_name["Q1"]
lattice.by_element_index[5]
lattice.by_element_key["Quadrupole"]  # all elements of that type
```

### TaylorMap
```python
from pytao.model import TaylorMap
tm = TaylorMap.from_tao(tao, ele1_id="start", ele2_id="end", order=2)
```

### Helper types
`ElementID`, `ElementRange`, `ElementList`, `ElementIntersection` — for
constructing element queries programmatically.

---

## SubprocessTao

Runs Tao in a separate process, sharing the same API as `Tao`. Useful for
loading multiple lattices simultaneously or isolating crashes.

```python
from pytao import SubprocessTao

with SubprocessTao(lattice_file="lattice.bmad") as tao:
    result = tao.cmd("show lat")
# subprocess closed and cleaned up automatically

# Manual lifecycle:
tao = SubprocessTao(lattice_file="lattice.bmad")
# ...
tao.close_subprocess()
```

Error handling is consistent between `Tao` and `SubprocessTao`.
Set `TAO_REUSE_SUBPROCESS=1` to reuse a single subprocess instance in tests.

---

## Tao Command Quick Reference

Sent via `tao.cmd("...")`. See the [Tao manual](https://www.classe.cornell.edu/bmad/tao.html)
for comprehensive documentation.

### Show commands
```
show lat [range]           — Lattice table
show ele <ele>             — Element details
show var <var>             — Variable info
show dat <dat>             — Data info
show global                — Global parameters
show universe              — Universe info
show orbit [range]         — Orbit
```

### Set commands
```
set ele <ele> <attr> = <val>   — Element attribute
set var <var>|model = <val>    — Variable value
set dat <dat>|meas = <val>     — Datum measurement
set global <param> = <val>     — Global parameter
set bmad_com <param> = <val>   — Bmad common parameter
```

### Action commands
```
use var <var>              — Enable variable for optimization
use dat <dat>              — Enable datum
veto var <var>             — Disable variable
veto dat <dat>             — Disable datum
run_optimizer              — Run optimizer
beam_track                 — Track beam
write bmad <file>          — Write lattice to file
```

### Element matching patterns
```
Q1                  — Named element
Quad::*             — All quadrupoles
1:10                — Elements 1 through 10
Q*                  — Wildcard match
Sextupole::S*       — Sextupoles starting with S
```

---

## Common Recipes

### Orbit correction
```python
tao.cmd("veto var *; veto dat *")
tao.cmd("use var orbit_correctors[*]")
tao.cmd("set dat orbit.x[*]|meas = 0; set dat orbit.y[*]|meas = 0")
tao.cmd("use dat orbit.x[*]; use dat orbit.y[*]")
tao.cmd("run_optimizer")
```

### Tune computation
```python
twiss_end = tao.ele_twiss("end")
tune_a = twiss_end["phi_a"]  # in units of 2π
tune_b = twiss_end["phi_b"]
```

### Floor plan extraction
```python
floor = [(e.head.name, e.floor.end.actual.x, e.floor.end.actual.z)
         for e in tao.eles("*")]
```

### Checkpoint and restore
```python
config = tao.get_config()
config.write("before_optimization.msgpack")

# ... do work ...

original = TaoConfig.from_file("before_optimization.msgpack")
original.set(tao)
```

### Write beam to file
```python
tao.cmd("write beam -at end beam_output.h5")
from pmd_beamphysics import ParticleGroup
P = ParticleGroup("beam_output.h5")
```
