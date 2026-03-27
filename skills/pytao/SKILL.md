---
name: pytao
description: >
  Use this skill when the user writes, debugs, or asks about Python code that interfaces with
  Tao/Bmad. Trigger on any mention of pytao or PyTao, `from pytao import Tao`, or when the
  user wants to do accelerator simulation tasks (tracking, Twiss parameters, beam optics,
  orbit, optimization, etc.) in Python or a Jupyter notebook. The key signal is the combination
  of Python context + Tao/Bmad/accelerator work. Do NOT trigger for pure Bmad lattice file
  syntax or Tao command-line usage without a Python context — those belong to the bmad and tao
  skills respectively.
---

# PyTao Skill

PyTao is the Python interface for **Tao**, the general-purpose accelerator simulation program
built on the **Bmad** toolkit. It wraps Tao's shared library (`libtao.so`) via ctypes, giving
Python full access to the Bmad/Tao simulation engine for charged-particle and X-ray simulations
in accelerators and storage rings.

PyTao requires **Python 3.10+** and **Bmad >= 20260317** compiled with `ACC_ENABLE_SHARED="Y"`.
It depends on `ormsgpack` and `orjson` for model serialization.

## When to read the reference

Before writing any non-trivial pytao code, read `references/api-reference.md` for method
signatures, common patterns, and pitfalls.

## Core principles

### 1. Initialization
Initialize Tao with keyword arguments:

```python
from pytao import Tao
tao = Tao(init_file="path/to/tao.init", noplot=True)
# or with a lattice file directly:
tao = Tao(lattice_file="path/to/lattice.bmad", noplot=True)
```

Use `noplot=True` for headless/scripting. Use `plot="mpl"` or `plot="bokeh"` for
PyTao-managed plotting. To load multiple lattices simultaneously, use `SubprocessTao`:

```python
from pytao import SubprocessTao
with SubprocessTao(lattice_file="lattice.bmad") as tao:
    print(tao.cmd("show lat"))
```

The `PYTAO_LIB_PATH` environment variable overrides automatic shared library detection.

### 2. Two API layers

**Low-level: `tao.cmd()` and typed methods** — `cmd()` sends raw Tao commands and returns
string output. The many `ele_*`, `lat_*`, `bunch_*` methods return structured Python
dicts and numpy arrays.

**High-level: Pydantic data models (`pytao.model`)** — `tao.ele("Q1")` returns a rich
`Element` object. `tao.get_config()` returns a `TaoConfig` capturing the full session
state. Settings sub-models (`BmadCom`, `BeamInit`, etc.) can be queried, modified, and
applied back — including via context managers for temporary changes.

### 3. Pydantic data models
All models are Pydantic v2 and support serialization to JSON, `.json.gz`, msgpack, and YAML.

**TaoConfig** captures the complete session state:
```python
config = tao.get_config()
config.beam_init.a_emit = 1e-8
config.set(tao)                    # apply all settings
config.set(tao, only_changed=True) # apply only what differs
```

**Settings sub-models** support context managers for temporary changes:
```python
from pytao.model import BeamInit
beam_init = BeamInit.from_tao(tao)
beam_init.a_emit = 1e-6
with beam_init.set_context(tao):
    # temporarily applied; auto-restored on exit
    tao.cmd("beam_track")
```

Available sub-models: `BmadCom`, `SpaceChargeCom`, `BeamInit`, `Beam`, `TaoGlobal`.

**The Element model** provides structured access to all element data:
```python
ele = tao.ele("Q00W")
ele.twiss.beta_a            # Twiss parameters
ele.attrs["k1"].data        # general attributes (note the .data accessor)
ele.floor.end.actual.x      # floor coordinates (hierarchy: ref/entrance/center/end × actual)
ele.orbit.x                 # orbit
ele.mat6.mat6               # 6x6 transfer matrix (numpy array)
```

**The Lattice model** collects elements with lookup by name, key, or index:
```python
from pytao.model import Lattice
lattice = Lattice.from_tao_unique(tao, ix_uni="1", ix_branch="0")
lattice.by_element_name["Q1"]
lattice.by_element_index[5]
lattice.by_element_key["Quadrupole"]
```

**All models serialize and deserialize:**
```python
config.write("state.msgpack")
config2 = TaoConfig.from_file("state.msgpack")
```

### 4. cmd() as escape hatch
When the high-level API doesn't cover something:
```python
tao.cmd("set ele Q1 k1 = 0.5")
result = tao.cmd("show lat 1:10")
```

For batch commands, `cmds()` suppresses intermediate lattice recalculations:
```python
tao.cmds([
    "set ele Q1 k1 = 0.5",
    "set ele Q2 k1 = -0.3",
], suppress_lattice_calc=True)
```

### 5. Extracting numeric data
Use typed methods rather than parsing `cmd()` output:
```python
twiss = tao.ele_twiss("Q1")           # dict: beta_a, alpha_a, etc.
orbit = tao.ele_orbit("Q1")           # dict: x, px, y, py, etc.
beta_a = tao.lat_list("*", who="ele.a.beta")  # numpy array across lattice
val = tao.evaluate("data::orbit.x[1]|model")  # evaluate expression
```

### 6. Plotting
```python
# Matplotlib backend
tao = Tao(init_file="tao.init", plot="mpl")
tao.plot("beta")

# Bokeh backend (best in Jupyter)
tao = Tao(init_file="tao.init", plot="bokeh")
tao.plot("beta")

# Handle startup script plotting conflicts:
from pytao import Tao, filter_tao_messages_context
with filter_tao_messages_context(functions=["tao_find_plots"]):
    tao = Tao(init_file="tao.init", plot="mpl")
```

For custom plots, extract data via `lat_list` and use matplotlib directly.

### 7. Beam tracking and particles
```python
tao.track_beam()                       # tracks beam with progress bar
tao.track_beam("start_ele", "end_ele") # tracks between specific elements

stats = tao.bunch_params("end")        # dict: emittances, sigmas, centroids
x = tao.bunch1("end", "x")            # numpy array of particle x positions

# ParticleGroup shortcut (requires openPMD-beamphysics):
P = tao.particles("end")
P.plot("x", "px")

# Raw openPMD-format dict (momenta in eV/c):
data = tao.bunch_data("end")
```

### 8. Session archiving
`archive()` writes a self-contained reproducible snapshot — the current lattice,
a Tao command file with all settings, and a bash launcher script:
```python
sh_file, cmd_file = tao.archive("output_dir/", prefix="my_run")
```

For finer control:
```python
config = tao.get_config()
config.write_bash_loader_script("output_dir/", tao=tao, prefix="my_run")
```

### 9. Error handling
All methods raise `RuntimeError` on Tao errors by default (`raises=True`).
Filtered pipe-command messages go to Python logging.
```python
try:
    tao.cmd("show ele nonexistent")
except RuntimeError as e:
    print(f"Tao error: {e}")

result = tao.cmd("show ele maybe_exists", raises=False)  # suppress errors
```

## Common patterns

### Scanning a parameter
```python
import numpy as np
results = []
for k1 in np.linspace(-1, 1, 50):
    tao.cmd(f"set ele Q1 k1 = {k1}")
    twiss = tao.ele_twiss("end")
    results.append({"k1": k1, "beta_a": twiss["beta_a"]})
```

### Lattice-wide Twiss extraction
```python
s = tao.lat_list("*", who="ele.s")
beta_a = tao.lat_list("*", who="ele.a.beta")
beta_b = tao.lat_list("*", who="ele.b.beta")
eta_x = tao.lat_list("*", who="ele.x.eta")
```

### Temporary beam settings via context manager
```python
from pytao.model import BeamInit
beam_init = BeamInit.from_tao(tao)
beam_init.a_emit = 1e-9
with beam_init.set_context(tao):
    tao.track_beam()
    stats = tao.bunch_params("end")
# original settings automatically restored here
```

### Multiple elements via pattern matching
```python
quads = tao.eles("Quad::*")
for q in quads:
    print(q.head.name, q.twiss.beta_a, q.attrs["k1"].data)
```

### Checkpoint and restore full session state
```python
config = tao.get_config()
config.write("checkpoint.msgpack")

# ... later ...
from pytao.model import TaoConfig
config = TaoConfig.from_file("checkpoint.msgpack")
config.set(tao)
```

## Pitfalls and tips

- **Shell variables**: Tao expands `$ACC_ROOT_DIR` etc. in init strings. Ensure
  the environment is configured or use absolute paths.
- **`quiet=True`** can break parts of PyTao. Avoid unless necessary.
- **Plotting conflicts**: If tao.init contains plotting commands and you use
  `plot="mpl"`, use `nostartup=True` or `filter_tao_messages_context`.
- **Momentum units**: Bmad normalizes momenta by reference momentum. `bunch_data()`
  and `particles()` return momenta in eV/c (openPMD convention).
- **`lat_list` returns numpy arrays** — vectorized math works directly.
- **General attributes** use the `.data` accessor: `ele.attrs["k1"].data`, not
  `ele.attrs["k1"]`.
- **Floor coordinates** follow a structured hierarchy:
  `ele.floor.end.actual.x` (position options: `reference`/`entrance`/`center`/`end`).
- **Batch changes**: Use `cmds()` with `suppress_lattice_calc=True` to avoid
  expensive intermediate lattice recalculations.
