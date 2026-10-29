# PyTao: using Tao from Python

PyTao gives Python access to Tao through its shared library. A `Tao` object
loads the model, accepts the same commands as the Tao prompt, and returns
calculated quantities as Python objects and arrays. This is also the usual
interface for an agent that needs to run a lattice or inspect a calculation.
The [Bmad guide](bmad.md) explains the physical model;
the [Tao guide](tao.md) explains commands, initialization, and session state.

The examples below follow PyTao's own documentation. Its full notebooks are
linked beside each topic; they include the lattice setup and longer analyses.

Contents: [session](#create-a-tao-session),
[commands and results](#commands-and-calculated-results),
[element models](#element-and-lattice-models), [scans](#scans-and-fitting),
[plots](#plotting), [particles](#beam-tracking-and-particles),
[configuration](#configuration-and-saved-state),
[independent sessions](#independent-sessions-and-diagnostics).

## Create a Tao session

The official [PyTao Basics](https://bmad-sim.github.io/pytao/examples/basic/)
notebook starts with the CESR example distributed with Bmad:

```python
from pytao import Tao

tao = Tao(
    init_file="$ACC_ROOT_DIR/bmad-doc/tao_examples/cesr/tao.init",
    noplot=True,
)
```

`init_file` loads a Tao configuration, including its lattice and any data,
variables, plots, and startup commands. The example path assumes an installed
Bmad distribution with `ACC_ROOT_DIR` set. For a project, use its own
`tao.init`. For a standalone lattice, use
`Tao(lattice_file="lattice.bmad", noinit=True, noplot=True)`; `noinit=True`
avoids loading a default initialization file.

Tao startup options are exposed as constructor keywords. `noplot=True`
suppresses the native plot window; Python plotting uses `plot="mpl"` or
`plot="bokeh"` instead. PyTao needs a working Tao shared library in addition
to the Python package. See [installation](https://bmad-sim.github.io/pytao/installation/)
for library discovery and [usage](https://bmad-sim.github.io/pytao/usage/)
for startup options and notebook integration.

## Commands and calculated results

`cmd` sends one Tao command and returns a list of output lines. It is useful
both for changing the model and for inspecting the same output a user sees
at the Tao prompt:

```python
print("\n".join(tao.cmd("show lattice 1:10")))
tao.cmd("set element Q00W x_offset = 1e-6")
orbit = tao.ele_orbit("Q00W")
```

Here `Q00W` is an element in the CESR example; use the corresponding name or
identifier in another lattice. Commands change the running Tao model. A later
query on the same object sees that model; edits are not automatically written
back into the original `.bmad` file. `cmds([...])` sends a sequence of commands.

PyTao provides several ways to retrieve results:

| Interface | What it supplies | Typical use |
| --- | --- | --- |
| `tao.cmd("show ...")` | Human-readable text lines | Inspect a command's output or diagnostic |
| `tao.ele_twiss(...)`, `tao.ele_orbit(...)` | Parsed dictionaries | Retrieve one kind of result at an element |
| `tao.lat_list(...)` | Arrays or lists across selected elements | Build a plot, table, or numerical calculation |
| `tao.evaluate(...)` | Numerical values of a Tao expression | Evaluate a derived quantity or data expression |
| `tao.ele(...)`, `tao.eles(...)` | Structured `Element` models | Explore several kinds of element information together |

For example:

```python
twiss = tao.ele_twiss("Q00W", which="model")
beta_a = twiss["beta_a"]
s = tao.lat_list("*", "ele.s")
beta_a_along_lattice = tao.lat_list("*", "ele.a.beta")
names = tao.lat_list("*", "ele.name")
```

`lat_list` returns numerical arrays for numerical quantities and a list of
strings for names. Its default flags select tracking elements; other flags
can change the selected objects and ordering. Use the same selection when
combining position and optics arrays. `evaluate` can return an array even
when an expression selects a single value.

The `a` and `b` labels are Bmad's transverse normal modes. They need not be
horizontal and vertical modes in a coupled lattice. Element queries normally
refer to the downstream end; selectors and lattice states follow
[Tao's addressing rules](tao/commands-and-scripts.md#select-elements-and-configurations).

The parsed methods use Tao's machine interface internally, so extracting
values does not require splitting the columns of `show lattice`. Raw
`cmd_real` and `cmd_integer` access numerical buffers populated by specific
Tao commands; they are not general conversions of arbitrary text output.
The [Basics notebook](https://bmad-sim.github.io/pytao/examples/basic/)
has sections on `lat_list`, method commands, and `pipe` internals. The
[Tao API](https://bmad-sim.github.io/pytao/api/tao/) documents Python conveniences
such as `ele`, `plot`, and `track_beam`. For an inherited command method not
listed there, use its docstring or search the
[generated command interface](https://github.com/bmad-sim/pytao/blob/master/pytao/interface_commands.py)
for its definition, such as `def ele_twiss` or `def lat_list`.

## Element and lattice models

`tao.ele()` gathers an element's metadata, attributes, optics, orbit, and other
information into an `Element` object. `tao.eles()` accepts a selection of
elements, including ranges, wildcards, and element types:

```python
ele = tao.ele("Q00W")
print(ele.name, ele.key, ele.twiss.beta_a)
print(ele.attrs["K1"].data, ele.attrs["K1"].units)

quads = tao.eles("quad::*", defaults=False, twiss=True, attrs=True)
```

The `.attrs` entries include values, units, and whether an attribute can be
changed. `.attribs` is a convenience view of their values. These objects
contain queried data; after a Tao command changes the model, query again for
updated results. Assigning a field in a returned data object does not itself
send a Tao command.

For a large lattice, requesting just the needed fields avoids querying all
available element information. The `Lattice` model collects `Element`
objects and provides lookup by name, type, or index, plus serialization.
The official [Elements and Lattices notebook](https://bmad-sim.github.io/pytao/examples/elements/)
demonstrates both models, field selection, and saving/loading. See the
[Element and Lattice API](https://bmad-sim.github.io/pytao/api/element/)
for the individual fields.

## Scans and fitting

A Python scan changes a lattice attribute or Tao variable, queries an
observable, and collects the results. The ordinary `Tao` object supports this
directly. Tao's optimizer can also be driven with `cmd`/`cmds`, then queried
through methods such as `merit`, `data`, and `var`.

Use the official [FODO optics notebook](https://bmad-sim.github.io/pytao/examples/fodo/)
for a complete example. It covers symmetric and asymmetric quadrupole scans,
fitting target beta functions, and subsequent beam tracking. Its initializer
loads the FODO lattice together with the data and variables used by the fit;
those names are specific to that setup. The [Tao fitting guide](tao/data-and-fitting.md)
explains how to define equivalent objects for another model.

Each scan point changes the current model. Preserve the starting values when
the scan is intended to be temporary. Tao normally recalculates after changes;
if calculations have been disabled globally or for a universe, queries can
return existing results instead of newly calculated optics. An unstable ring
can also fail to produce valid periodic optics. These are properties of the
Tao model, not of the Python loop.

## Plotting

PyTao can render Tao plot templates using Matplotlib or Bokeh. This example
follows the official Matplotlib notebook:

```python
tao = Tao(
    init_file="$ACC_ROOT_DIR/bmad-doc/tao_examples/optics_matching/tao.init",
    plot="mpl",
)
tao.plot("beta", save="beta.png", include_layout=False)
```

Templates such as `beta`, `dispersion`, `orbit`, and `floor_plan` define what
to plot. PyTao supplies the Python rendering and options for layout and
appearance. Arrays from `lat_list` can also be plotted directly with ordinary
Python plotting tools.

Use the [Matplotlib notebook](https://bmad-sim.github.io/pytao/examples/plot-matplotlib/)
for stacked plots, fields, figure customization, and saving figures, or the
[Bokeh notebook](https://bmad-sim.github.io/pytao/examples/plot-bokeh/)
for interactive plots. A startup file that issues native plotting commands
may need a version without those commands when using Python plotting; see
[plotting and startup scripts](https://bmad-sim.github.io/pytao/usage/#pytao-plotting-and-startup-scripts).

## Beam tracking and particles

Beam tracking requires a particle distribution and beam settings in Tao.
`track_beam()` runs that calculation; it does not infer the bunch properties
from the lattice's reference particle. With a configured beam:

```python
tao.track_beam(use_progress_bar=False)
stats = tao.bunch_params("END")
x = tao.bunch1("END", "x")
particles = tao.particles("END")
```

`bunch_params` supplies statistics, while `bunch1` supplies individual particle
coordinates in Bmad's convention. Full particle access requires the beam to
have been saved at the requested element. `particles` returns an
`openPMD-beamphysics` `ParticleGroup`; its momenta use eV/c rather than Bmad's
reference-normalized momentum coordinates. `bunch_data` supplies the
corresponding dictionary of arrays. See [physics conventions](bmad/physics-conventions.md)
when translating between these representations.

The [Bunch Commands notebook](https://bmad-sim.github.io/pytao/examples/bunch/)
shows statistics, particle arrays, initial-particle access, and cumulative
beam data. The [beam tracking notebook](https://bmad-sim.github.io/pytao/examples/beam_track_progress_bar/)
shows how to configure a Gaussian distribution and track it with progress
reporting.

## Configuration and saved state

`TaoConfig` represents startup settings, common physics settings, beam
initialization, tracking settings, globals, and element overrides. It can
generate Tao commands or apply its settings back to a session:

```python
config = tao.get_config()
config.beam_init.a_emit = 2e-8
config.beam_init.set(tao, only_changed=True)
config.write("beam_configuration.json")
```

Changing the Python configuration object and applying it are separate actions.
A saved configuration is also distinct from the lattice it refers to.
`tao.archive("my_archive")` writes a lattice snapshot, a Tao settings command
file, and a shell launcher together. The official
[TaoConfig notebook](https://bmad-sim.github.io/pytao/examples/config/)
covers changing, saving, and loading configurations and creating an archive;
the [configuration API](https://bmad-sim.github.io/pytao/api/config/)
describes individual settings models.

## Independent sessions and diagnostics

There is one native Tao state per Python process. Constructing another `Tao`
object reinitializes that state; two Python variables do not provide two
independent models. Use `SubprocessTao` when independent simultaneous sessions
are needed:

```python
from pytao import SubprocessTao

with SubprocessTao(init_file="other_model/tao.init", noplot=True) as other:
    optics = other.ele_twiss("END")
```

The context manager closes the process on exit. See
[SubprocessTao usage](https://bmad-sim.github.io/pytao/usage/#subprocesstao-tao-in-a-subprocess)
for lifetime management.

Tao errors normally raise Python exceptions. Their messages retain the Tao
diagnostic. `raises=False` is available for inspecting raw error output, but
does not make a failed calculation valid. The usage guide also documents
[Python logging](https://bmad-sim.github.io/pytao/usage/#logging).
Avoid `quiet=True` as a general logging control: the upstream usage guide
notes that it can interfere with PyTao behavior.
