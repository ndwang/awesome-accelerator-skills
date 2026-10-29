# Tao initialization

`tao.init` describes a Tao session: which lattices to load, what data and variables
to define, and how to initialize plots or particle bunches. The `.bmad` file
describes the physical lattice. A Tao command file contains operations to execute
after initialization. These are three different input languages and roles.

## A small initialization file

Put this `tao.init` beside a Bmad file named `lattice.bmad`:

```fortran
&tao_design_lattice
  n_universes = 1
  design_lattice(1)%file = "lattice.bmad"
/
```

Start it with:

```sh
tao -init_file tao.init -noplot
```

The same session can be opened with `Tao(init_file="tao.init", noplot=True)` in
[PyTao](../pytao.md). An initialization file is useful as soon as the session needs
more than a lattice. For a lattice alone, `tao -lat lattice.bmad -noinit` is enough.

## Namelist syntax

Tao initialization uses Fortran **namelists**. `&name` starts a block, `/` ends
it, `%` accesses a structure component, and `(N)` selects an array entry.
Strings should be quoted; `!` introduces a comment. Logical values can be
written as `T` and `F`.

Unlike Bmad lattice expressions, namelist values are not arithmetic expressions.
Write a computed number such as `0.025`, not `1/40`: the slash would end the
namelist. Array assignment consumes the values supplied; one value does not
broadcast across a range. These distinctions matter when translating a Bmad
expression into an initialization setting.

Source: [Initialization][init], “Namelist Syntax” (`s:format`).

## What goes in each block

| Namelist | Purpose |
| --- | --- |
| `tao_start` | Locate other initialization files and startup command files |
| `tao_design_lattice` | Select the lattice for each universe |
| `tao_params` | Set global Tao and Bmad calculation parameters |
| `tao_d2_data`, `tao_d1_data` | Define named data groups and individual observables/targets |
| `tao_var` | Define adjustable lattice parameters |
| `tao_beam_init` | Define the tracked bunch and where particle coordinates are saved |
| `tao_plot_page` | Place plots into regions on the native plot page |
| `tao_template_plot`, `tao_template_graph` | Define custom plots and their graphs/curves |

A small project can keep these blocks in `tao.init`. Larger projects can separate
them by role:

```fortran
&tao_start
  data_file = "data.init"
  var_file = "variables.init"
  plot_file = "plots.init"
  startup_file = "setup.tao"
/

&tao_design_lattice
  design_lattice(1)%file = "lattice.bmad"
/
```

Without an explicit `data_file`, `var_file`, `beam_file`, or `plot_file`, Tao
looks for those namelists in the root initialization file. `startup_file`
names executable Tao commands, not namelists; the default name is `tao.startup`.
For example, the bundled [matching setup](../../assets/matching/tao.init) uses
`setup.tao` to define an optimizer alias.

Paths specified inside the root initialization file are relative to its
directory. Paths passed on the command line are relative to the process working
directory, and command-line selections take precedence. `-nostartup` skips
startup commands; `-noplot` suppresses the native window but does not itself
remove commands from a startup file.

One naming trap: `-lattice_file` on the command line selects a physical lattice.
The `lattice_file` field in `tao_start` selects the file containing the
`tao_design_lattice` namelist. The latter then names the `.bmad` files.

Source: [Initialization][init], “Beginning Initialization” (`s:init.begin`) and
“Lattice Initialization” (`s:init.lat`).

## Multiple universes

The official [multiple-universes example][universes] loads two configurations:

```fortran
&tao_design_lattice
  n_universes = 2
  design_lattice(1)%file = "lat1.bmad"
  design_lattice(2)%file = "lat2.bmad"
/
```

Each universe has its own data and model/design/base lattices. A Tao variable
can link the same adjustable attribute across universes, which is useful when
fitting several measurement conditions with one set of magnet parameters.
See [Tao concepts](../tao.md) and [data and fitting](data-and-fitting.md).

## Beam initialization

Lattice optics and a tracked particle distribution are different objects.
`tao_beam_init` specifies the latter. The official
[beam-tracking example][beam] includes settings such as:

```fortran
&tao_beam_init
  saved_at = "*"
  beam_init%n_particle = 1000
  beam_init%a_norm_emit = 1.0e-6
  beam_init%b_norm_emit = 1.0e-6
  beam_init%bunch_charge = 1e-9
  beam_init%sig_pz = 1e-3
  beam_init%sig_z = 0.00059958
/
```

The emittances here are normalized, `bunch_charge` is in coulombs, `sig_pz` is
the spread in Bmad's relative momentum coordinate, and `sig_z` is in meters.
`saved_at` chooses locations whose particle coordinates remain available after
tracking; `"*"` saves at every element and can be expensive for a large model.
Use the full upstream example for its lattice, plot definitions, and command
files. Distribution choices and coordinate meanings are defined in the manual.

## Further details

Search the following sections in [the initialization source][init]:

| Topic | Section label |
| --- | --- |
| Startup options | `s:command.line` |
| Global parameters | `s:globals` |
| Bunch distributions, Twiss parameters, species, and saved locations | `s:beam.init` |
| Variable definitions | `s:init.var` |
| Data definitions | `s:init.data` |
| Plot page and templates | `s:init.plot`, `s:plot.page`, `s:template` |

[init]: https://github.com/bmad-sim/bmad-ecosystem/blob/main/tao/doc/initialization.tex
[universes]: https://github.com/bmad-sim/bmad-ecosystem/tree/main/bmad-doc/tutorial_bmad_tao/lattice_files/multiple_universes
[beam]: https://github.com/bmad-sim/bmad-ecosystem/tree/main/bmad-doc/tutorial_bmad_tao/lattice_files/beam_tracking
