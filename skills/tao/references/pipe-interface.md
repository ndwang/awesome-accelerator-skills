# Tao Reference: Pipe Interface

Tao provides a programmatic interface for communicating with external programs
and scripting languages, primarily Python. The key components are the `pipe`
command (built into Tao) and the `PyTao` package (a Python interface layer).

## PyTao Interface

The `PyTao` package is hosted on GitHub independently of Bmad distributions:

```
https://bmad-sim.github.io/pytao
```

See the PyTao documentation for installation instructions and detailed examples.

### Ctypes vs Pexpect

PyTao supports two connection methods:

**ctypes** -- Uses Python's foreign function library to link directly to a Tao
shared-object library.

- Advantage: Direct access to Tao code; more robust communication.
- Disadvantage: Requires a shared-object build of the Tao library.

**pexpect** -- Uses a general-purpose Python module for spawning and
controlling child processes.

- Advantage: Works with any standard Tao executable; no shared library needed.
- Disadvantage: Slower; can time out waiting for a response from Tao.

### PyTao via Pexpect

The `tao_pipe.py` module is provided by PyTao in the `pytao/tao_pexpect` directory.

```python
>>> from pytao.tao_pexpect import tao_pipe  # import module
>>> p = tao_pipe.tao_io("-lat my_lat.bmad") # init session
>>> out = p.cmd_in("show global")           # Command to Tao
>>> print(out)                              # print the output from Tao
>>> p.cmd("show global")                    # Like p.cmd_in() except prints the output too.
```

### PyTao via Ctypes

The `pytao.py` module for ctypes-based interfacing is provided by PyTao in the
`pytao/tao_pexpect` directory. A test driver script `pytao_example.py` is
included in the same directory. See the documentation in both files for further
information.

## Tao's Pipe Command

The `pipe` command was developed to:

- Standardize output of information (data, parameters, etc.) from Tao to
  simplify interfacing to external programs, especially scripting languages
  like Python.
- Act as an intermediate layer for controlling Tao from things like machine
  online control programs or graphical user interfaces.

Using `pipe` is far superior to using `show` when interfacing to an external
program. The `pipe` command output is formatted for ease of parsing, and its
format is much more stable over time than `show` output. The risk of
user-developed interface code breaking is much reduced by using `pipe`.

The general form is:

```
pipe <subcommand> <arguments>
```

The `pipe` command has over 100 subcommands divided into two categories:

- **Action** subcommands: allow controlling Tao (e.g., creating variables and
  data for optimization).
- **Output** subcommands: output information from Tao.

## Pipe Output Format

Output is semicolon-delimited. Most output subcommands use "parameter list
form" where each line has four fields:

```
{name};{type};{can_vary};{value(s)}
```

Example output from `pipe global`:

```
lm_opt_deriv_reinit;REAL;T; -1.0000000000000000E+00
de_lm_step_ratio;REAL;T;  1.0000000000000000E+00
de_var_to_population_factor;REAL;T;  5.0000000000000000E+00
unstable_penalty;REAL;T;  1.0000000474974513E-03
n_opti_cycles;INT;T;20
track_type;ENUM;T;single
derivative_uses_design;LOGIC;T;F
... etc ...
```

### Field Descriptions

**name** -- The name of the parameter.

**type** -- The type of the parameter. Possible values:

| Type Code    | Description |
|--------------|-------------|
| `INT`        | Integer number |
| `REAL`       | Real number |
| `COMPLEX`    | Complex number, output as `Re;Im` |
| `REAL_ARR`   | Real array |
| `LOGIC`      | Logical: `T` or `F` |
| `INUM`       | Integer whose allowed values can be obtained using `pipe inum` |
| `ENUM`       | String whose allowed values can be obtained using `pipe enum` |
| `FILE`       | Name of file |
| `CRYSTAL`    | Crystal name string, e.g. `Si(111)` |
| `DAT_TYPE`   | Data type string, e.g. `orbit.x` |
| `DAT_TYPE_Z` | Data type string if `plot%x_axis_type = 'data'`; otherwise a `data_type_z` enum |
| `SPECIES`    | Species name string, e.g. `H2SO4++` |
| `ELE_PARAM`  | Lattice element parameter string, e.g. `K1` |
| `STR`        | String that does not fall into another string category |
| `STRUCT`     | Structure: `{name1};{type1};{value1};{name2};{type2};{value2};...` |
| `COMPONENT`  | For curve component parameters |

**can_vary** -- Either `T`, `F`, or `I`, indicating whether the user may
change the value. `I` indicates the parameter should be ignored by a GUI when
displaying parameters.

**value(s)** -- The value or values of the parameter. Multiple values (e.g. an
array) are separated by semicolons.

## Plotting Issues

When using Tao with a GUI that handles its own plotting, the `-noplot` and
`-external_plotting` options should be used when starting Tao.

- `-noplot` (sets `global%plot_on`) prevents Tao from opening a plotting
  window. Both options can also be set after startup with `set global` and
  viewed with `show global`.
- With `-external_plotting` set, the external code handles plot assignment to
  regions. The `place` command will not perform placement but instead saves its
  arguments to a buffer readable via `pipe place_buffer`. The external code
  can bypass buffering using `place` with the `-no_buffer` switch.

Normally when `-noplot` is active, Tao skips calculating plot curve points to
save time. The exception is when `-external_plotting` is also on.

To make plot references unambiguous, plots can be referred to by index number
(viewable via `pipe plot_list`):

- `@Tnnn` -- references template plot with index `nnn` (e.g. `@T3`)
- `@Rnnn` -- references displayed (region) plot with index `nnn`

## Pipe Subcommands

The subcommands are organized below by category. Each entry shows the
subcommand name and a brief description.

### Data and Variables

| Subcommand | Description |
|------------|-------------|
| `beam` | Output beam parameters not in the `beam_init` structure |
| `beam_init` | Output `beam_init` parameters |
| `bunch_comb` | Output bunch parameters at a comb point |
| `bunch_params` | Output bunch parameters at exit end of a lattice element |
| `bunch1` | Output bunch parameters at exit end of a lattice element (single bunch) |
| `constraints` | Output optimization data and variable parameters contributing to the merit function |
| `da_aperture` | Output dynamic aperture data |
| `da_params` | Output dynamic aperture input parameters |
| `data` | Output individual datum parameters |
| `data_d_array` | Output list of datums for a given `d1_data` structure |
| `data_d1_array` | Output list of `d1` arrays for a given `data_d2` |
| `data_d2` | Output information on a `d2_datum` |
| `data_d2_array` | Output `data_d2` info for a given universe |
| `data_d2_create` | Create a `d2` data structure with associated `d1` and data arrays |
| `data_d2_destroy` | Destroy a `d2` data structure with associated `d1` and data arrays |
| `data_parameter` | Output an array of values for a particular datum parameter |
| `data_set_design_value` | Set design (and base) values of all datums to design lattice values |
| `datum_create` | Create a datum |
| `datum_has_ele` | Output whether a datum type has an associated lattice element |
| `derivative` | Output optimization derivatives |
| `evaluate` | Output the value of an expression (result may be a vector) |
| `merit` | Output merit value |
| `var` | Output parameters of a given variable |
| `var_create` | Create a single variable |
| `var_general` | Output list of all variable `v1` arrays |
| `var_v_array` | Output list of variables for a given `data_v1` |
| `var_v1_array` | Output list of variables in a given variable `v1` array |
| `var_v1_create` | Create a `v1` variable structure with associated var array |
| `var_v1_destroy` | Destroy a `v1` var structure with associated var sub-array |
| `wave` | Output wave analysis info |

### Lattice and Elements

| Subcommand | Description |
|------------|-------------|
| `bmad_com` | Output `bmad_com` structure components |
| `branch1` | Output lattice branch information for a particular branch |
| `ele:ac_kicker` | Output element `ac_kicker` parameters |
| `ele:cartesian_map` | Output element `cartesian_map` parameters |
| `ele:chamber_wall` | Output element beam chamber wall parameters |
| `ele:control_var` | Output list of element control variables (group, overlay, ramper) |
| `ele:cylindrical_map` | Output element `cylindrical_map` parameters |
| `ele:elec_multipoles` | Output element electric multipoles |
| `ele:floor` | Output element floor coordinates |
| `ele:gen_attribs` | Output element general attributes |
| `ele:gen_grad_map` | Output element `gen_grad_map` parameters |
| `ele:grid_field` | Output element `grid_field` parameters |
| `ele:head` | Output "head" element attributes |
| `ele:lord_slave` | Output the lord/slave tree of an element |
| `ele:mat6` | Output element `mat6` transfer matrix |
| `ele:methods` | Output element methods |
| `ele:multipoles` | Output element multipoles |
| `ele:orbit` | Output element orbit |
| `ele:param` | Output lattice element parameter |
| `ele:photon` | Output element photon parameters |
| `ele:spin_taylor` | Output element `spin_taylor` parameters |
| `ele:taylor` | Output element Taylor map |
| `ele:twiss` | Output element Twiss parameters |
| `ele:wake` | Output element wake parameters |
| `ele:wall3d` | Output element `wall3d` parameters |
| `em_field` | Output EM field at a given point generated by a given element |
| `enum` | Output list of possible values for enumerated numbers |
| `inum` | Output list of possible values for an `INUM` parameter |
| `lat_branch_list` | Output lattice branch list |
| `lat_calc_done` | Output if a lattice recalculation has been performed since last check |
| `lat_ele_list` | Output lattice element list |
| `lat_header` | Output lattice header info (lattice name, machine name, etc.) |
| `lat_list` | Output list of parameters at ends of lattice elements |
| `lat_param_units` | Output units of a parameter associated with a lattice or element |
| `lord_control` | Output lord information for a given slave element |
| `matrix` | Output transfer matrix from exit end of one element to another |
| `orbit_at_s` | Output Twiss at a given s position |
| `ring_general` | Output lattice branch with closed geometry info (emittances, etc.) |
| `slave_control` | Output slave information for a given lord element |
| `species_to_int` | Convert species name to corresponding integer |
| `species_to_str` | Convert species integer id to corresponding name |
| `super_universe` | Output `super_universe` parameters |
| `taylor_map` | Output Taylor map between two points |
| `twiss_at_s` | Output Twiss parameters at a given s position |
| `universe` | Output universe info |
| `wall3d_radius` | Output vacuum chamber wall radius for given s-position and angle |

### Plotting

| Subcommand | Description |
|------------|-------------|
| `building_wall_graph` | Output (x, y) points for drawing a building wall for a graph |
| `building_wall_list` | Output list of building wall sections or section points |
| `building_wall_point` | Output building wall point parameters |
| `building_wall_section` | Add or delete a building wall section |
| `floor_plan` | Output (x, y) points and info for drawing a floor plan |
| `floor_orbit` | Output (x, y) coordinates for drawing the orbit on a floor plan |
| `place_buffer` | Output the place command buffer and reset the buffer |
| `plot_curve` | Output curve information for a plot |
| `plot_curve_manage` | Template plot curve creation/destruction |
| `plot_graph` | Output graph info |
| `plot_graph_manage` | Template plot graph creation/destruction |
| `plot_histogram` | Output plot histogram info |
| `plot_lat_layout` | Output plot lat_layout info |
| `plot_line` | Output points used to construct the line of a plot curve |
| `plot_list` | Output list of plot templates or plot regions |
| `plot_symbol` | Output locations to draw symbols for a plot curve |
| `plot_template_manage` | Template plot creation or destruction |
| `plot_transfer` | Transfer plot parameters from one plot to another |
| `plot1` | Output info on a given plot |
| `shape_list` | Output `lat_layout` or `floor_plan` shapes list |
| `shape_manage` | Element shape creation or destruction |
| `shape_pattern_list` | Output list of shape patterns or shape pattern points |
| `shape_pattern_manage` | Add or remove shape pattern |
| `shape_pattern_point_manage` | Add or remove shape pattern point |
| `shape_set` | Set `lat_layout` or `floor_plan` shape parameters |

### Global and Miscellaneous

| Subcommand | Description |
|------------|-------------|
| `global` | Output global parameters |
| `global:optimization` | Output optimization parameters |
| `global:opti_de` | Output DE (differential evolution) optimization parameters |
| `help` | Output list of `help xxx` topics |
| `ptc_com` | Output `ptc_com` structure components |
| `show` | Output the output from a `show` command |
| `space_charge_com` | Output `space_charge_com` structure parameters |
| `spin_invariant` | Output closed orbit spin axes at ends of all lattice elements |
| `spin_polarization` | Output spin polarization information |
| `spin_resonance` | Output spin resonance information |

## Structured Command Data

Structured pipe command data (machine-readable JSON format) is available at:

```
docs/tao/doc/pipe-interface-commands.json
```

This JSON file can be used to programmatically inspect argument syntax,
optional flags, and output formats for each pipe subcommand.
