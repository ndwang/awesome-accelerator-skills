---
name: tao
description: Reference guide for Tao (Tool for Accelerator Optics), the user-facing program for accelerator simulation built on the Bmad library. PyTao is the Python interface to Tao. Use this skill whenever the user works with Tao commands (show, set, place, run_optimizer, etc.), Tao init files, Tao data/variables/optimization, Tao plotting, the Tao pipe interface, or PyTao scripts.
---

# Tao: Tool for Accelerator Optics

Tao is a general-purpose program for simulating high-energy particle beams in accelerators and
storage rings. It is built on the Bmad simulation library. Applications include single/multiparticle
tracking, lattice simulation and analysis, lattice design, and machine commissioning/correction.

- Website: classe.cornell.edu/bmad
- PyTao (Python interface): bmad-sim.github.io/pytao/
- Tutorial: Available from the Bmad web page (separate from this reference)

## Starting Tao

```
tao {OPTIONS}
```

Key startup options:

| Option | Description |
|--------|-------------|
| `-lattice_file <file>` | Lattice file (`.bmad`). Required if no init file. |
| `-init_file <file>` | Initialization file (default: `tao.init`). |
| `-noinit` | Skip init file. Requires `-lattice_file`. |
| `-noplot` | Suppress plot window. |
| `-command "<cmds>"` | Commands to run at startup (semicolon-separated). |
| `-geometry <W>x<H>` | Plot window size in points. |
| `-beam_file <file>` | Beam initialization file. |
| `-data_file <file>` | Data definition file. |
| `-var_file <file>` | Variable definition file. |
| `-plot_file <file>` | Plot definition file. |
| `-nostartup` | Skip `tao.startup` command file. |
| `-rf_on` | Turn RF cavities on. |
| `-symbol_import` | Import lattice symbols as Tao variables. |
| `-reverse` | Reverse lattice element order. |

Example:
```
tao -init my.init -lat ring.bmad -command "show lat 1:10; quit"
```

## Core Concepts

### Data Model Hierarchy

**Super_universe** (top level) contains:
- One or more **universes** (each holds a machine lattice + data)
- **Variables** (shared across universes, control lattice parameters)
- **Plotting** information
- **Global parameters**

### Three Lattice Types (per universe)

| Lattice | Purpose |
|---------|---------|
| **Design** | Fixed reference from the lattice file. Never modified. |
| **Model** | Working copy. Modified during optimization. Initially = design. |
| **Base** | User-settable reference for comparing changes. Initially = design. |

### Data Hierarchy

- **d2_data** -- top-level group (e.g., `orbit`)
- **d1_data** -- sub-group (e.g., `x` for horizontal)
- **datum** -- individual data point (e.g., `orbit.x[10]`)

Referencing: `{[universe]@}d2_name.d1_name[index_list]{|component}`
Example: `2@orbit.x[3:10]|meas`

### Variables

A **variable** controls a lattice parameter (e.g., quadrupole `k1`). Variables are grouped in
**v1_var** arrays. Reference: `var_name[index]{|component}`

Example: `quad_k1[3:6,23]` or `quad_k1[q03:q06,q23]` (by element name)

### Universe Specification

Format: `[universe_range]@parameter`

```
2@orbit.x         -- orbit.x in universe 2
[2:4,7]@orbit.x   -- universes 2,3,4,7
*@orbit.x          -- all universes
orbit.x            -- default universe
```

## Command Syntax

- Commands are **case sensitive** (but element names are not)
- `;` separates multiple commands on one line
- `!` starts a comment
- `&` at end of line continues to next line
- `{}` in syntax = optional, `<>` = substitute appropriate value
- Use `help <command>` to get documentation on any command

### Element Specification

```
Q3           -- element named Q3
Q3##2        -- 2nd element named Q3
134          -- element with index 134
1>>13        -- element 13 in branch 1
2@1>>TZ      -- element TZ in branch 1, universe 2
```

### Element List Format

```
23, 45:74, quad::q*    -- index, range, class::wildcard
```

Wildcards: `*` matches any characters, `%` matches one character.

### Expressions

Operators: `+`, `-`, `*`, `/`, `^` (exponentiation)

Functions: `sqrt`, `log`, `exp`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`,
`abs`, `int`, `nint`, `floor`, `ceiling`, `modulo`, `factorial`,
`ran()`, `ran_gauss()`, `average(arr)`, `rms(arr)`, `sum(arr)`, `min(arr)`, `max(arr)`

### Parameter Token Types

| Prefix | Meaning | Example |
|--------|---------|---------|
| `data::` | User-defined data | `data::orbit.x[4]|meas` |
| `var::` | Variables | `var::quad_k1[5]|model` |
| `lat::` | Lattice parameters (computed) | `lat::orbit.x[q10w]|model` |
| `beam::` | Beam tracking results | `beam::sigma.x[q10w]` |
| `ele::` | Element parameters (exit end) | `ele::Q01W[k1]` |
| `ele_mid::` | Element parameters (middle) | `ele_mid::34[orbit_x]` |

Use `show value <expression>` to evaluate any expression.

## Essential Commands

### show -- Display information

```
show lattice {ele_list} {options}    -- element-by-element table
show element <ele> {options}         -- detailed element info (-all for all attributes)
show data {d2_name.d1_name}          -- data values and status
show variable {var_name}             -- variable values and status
show global {options}                -- global parameters (-bmad_com, -ptc_com, etc.)
show plot {plot_name}                -- plot info (-page for page params)
show merit                           -- top contributors to merit function
show constraints                     -- optimization constraints
show value <expression>              -- evaluate an expression
show optimizer                       -- optimizer parameters
show emittance                       -- normal mode emittances
show chromaticity                    -- chromaticity and momentum compaction
```

Output to file: `show -write <file> ...` or `show -append <file> ...`

### set -- Set parameter values

```
set element <ele_list> <attr> = <value>         -- set element attribute
set data <name>|<component> = <value>           -- set data component
set variable <name>|<component> = <value>       -- set variable component
set global <param> = <value>                    -- set global parameter
set default universe = <n>                      -- set default universe
set default branch = <n>                        -- set default branch
set lattice {n@}<dest_lat> = <source_lat>       -- copy between lattices
set particle_start {n@}<coord> = <value>        -- set initial particle coords
set beam_init {n@}<param> = <value>             -- set beam initialization
set curve <curve> <param> = <value>             -- set curve parameter
set graph <graph> <param> = <value>             -- set graph parameter
set plot <plot> <param> = <value>               -- set plot parameter
set region <region> <param> = <value>           -- set region parameter
```

### change -- Modify element/variable values

```
change element <ele_list> <attribute> <delta>   -- change by delta
change variable <name>[<idx>] <delta>           -- change variable by delta
change particle_start <coord> <delta>           -- change starting coords
```

Prefix `<delta>` with `@` to set absolute value: `change var quad_k1[5] @0.1`

### place -- Assign plots to regions

```
place <region> <plot_name>     -- place a template plot in a region
place -no_buffer <region> <plot_name>  -- bypass GUI buffer
```

Example: `place r13 beta` places the beta function plot in region r13.

### scale / x_scale / x_axis

```
scale <plot_or_graph> <y_min> <y_max>    -- set y-axis scale
scale <plot_or_graph>                     -- auto-scale y-axis
x_scale <plot_or_graph> <x_min> <x_max>  -- set x-axis scale
x_scale <plot_or_graph>                   -- auto-scale x-axis
x_axis <plot_or_graph> <x_axis_type>      -- set x-axis type (s, index, ele_index)
```

### run_optimizer -- Run optimization

```
run_optimizer {<optimizer>}     -- run optimizer (default if none specified)
```

Optimizers: `lm` (Levenberg-Marquardt), `lmdif`, `geodesic_lm`, `de` (differential evolution),
`svd`, `custom`. Press `.` to stop.

### use / veto / restore -- Control data/variables in optimization

```
use data <d2_name>{.d1_name}        -- include data in optimization
use var <v1_name>                    -- include variable in optimization
veto data <d2_name>{.d1_name}       -- exclude data from optimization
veto var <v1_name>                   -- exclude variable from optimization
restore data <d2_name>{.d1_name}    -- restore data to optimization
restore var <v1_name>                -- restore variable to optimization
```

### write -- Output to files

```
write bmad {-format <fmt>} <file>      -- write model lattice as Bmad file
write lattice_file <file>              -- write lattice file
write beam <file>                      -- write beam data
write ps <file>                        -- write plot as PostScript
write pdf <file>                       -- write plot as PDF
write gif <file>                       -- write plot as GIF
```

### Other frequently used commands

```
alias {<name> <string>}               -- define command alias
call <file> {args}                     -- execute command file
help {<topic>}                         -- show help on a command
derivative                             -- recalculate derivative matrix
reinitialize {data|variable|plot}      -- reinitialize from files
read {lattice|beam|...} <file>         -- read in data from file
quit                                   -- exit Tao
```

### Command files and do loops

```
call my_script.tao arg1 arg2     -- call command file (args accessed as [[1]], [[2]])

do i = 1, 100
  set element quad[[[i]]] k1 = 0.1 * [[i]]
enddo
```

Speed up batch operations:
```
set global lattice_calc_on = F   -- disable recalculation
set global quiet = all           -- suppress output
... batch operations ...
set global lattice_calc_on = T   -- re-enable
set global quiet = off
```

## Data & Variables Quick Reference

**Defining data** requires initialization files using Fortran namelists (`tao_d2_data`,
`tao_d1_data`). Each datum has:
- `data_type` -- what to compute (e.g., `orbit.x`, `beta.a`, `emit.b`)
- `ele_name` -- evaluation element
- `merit_type` -- how it enters optimization: `target`, `min`, `max`, `abs_min`, `abs_max`
- `weight` -- merit function weight
- `meas` -- measured/desired value
- `data_source` -- `lat` (single particle) or `beam` (multi-particle)

**Common data types**: `orbit.x/.y/.px/.py`, `beta.a/.b`, `alpha.a/.b`, `eta.x/.y`,
`etap.x/.y`, `phase.a/.b`, `emit.a/.b`, `cbar.11/.12/.21/.22`, `sigma.*`,
`floor.x/.y/.z`, `chrom.a/.b`, `r.ij` (transfer matrix), `s_position`,
`expression:<expr>`, `unstable.orbit/.lattice`

**Defining variables** uses the `tao_var` namelist. Each variable has:
- `ele_name` / `attrib_name` -- what lattice parameter to control
- `step` -- small change for derivative computation
- `weight` -- merit function weight
- `high_lim` / `low_lim` -- bounds
- `merit_type` -- `target` or `limit`

See `references/data.md` for full datum component lists and data types table.
See `references/variables.md` for full variable component lists.
See `references/initialization.md` for namelist syntax.

## Plotting Quick Reference

Hierarchy: **plot_page** > **region** > **plot** > **box** > **graph** > **curve**

**Graph types**: `data`, `floor_plan`, `lat_layout`, `phase_space`, `histogram`,
`dynamic_aperture`, `key_table`, `wave.0`, `wave.a`, `wave.b`

**Curve components**: `model`, `design`, `base`, `meas`, `ref` (or combinations like
`model-design`)

Key commands:
```
place r13 beta              -- place beta plot in region r13
scale r13 0 50              -- set y-axis range
x_scale r13 0 100           -- set x-axis range
set graph r13.g component = model-design    -- change what's plotted
set curve r13.g.c1 draw_symbols = T         -- show data points
```

See `references/plotting.md` for full details.

## Optimization Quick Reference

Merit function: `M = Sum_i w_i [delta_D_i]^2 + Sum_j w_j [delta_V_j]^2`

Where `delta_D` depends on `merit_type` and the composite value expression:

| opt_with_ref | opt_with_base | Composite Expression |
|:---:|:---:|---|
| F | F | model - meas |
| F | T | model - meas - base |
| T | F | (model - meas) - (design - ref) |
| T | T | (model - meas) - (base - ref) |

Workflow:
1. Define data and variables in initialization files
2. `use data <name>` / `use var <name>` to select what to optimize
3. `run_optimizer {lm|de|geodesic_lm|svd}` to run
4. `show merit` to see top contributors
5. `show constraints` to check constraint satisfaction

See `references/optimization-and-wave.md` for details.

## Pipe/Python Interface Quick Reference

PyTao provides Python access to Tao via the `pipe` command:

```python
from pytao import Tao
tao = Tao("-lat ring.bmad")
output = tao.cmd("show global")
```

Pipe output is semicolon-delimited: `name;type;can_vary;value`

Types: `INT`, `REAL`, `LOGIC`, `ENUM`, `STR`, `STRUCT`, `REAL_ARR`, `COMPLEX`

Key pipe subcommands (use `pipe <subcommand>`):
- **Lattice**: `lat_ele_list`, `lat_branch_list`, `lat_list`, `lat_param_units`
- **Elements**: `ele:head`, `ele:param`, `ele:orbit`, `ele:twiss`, `ele:floor`
- **Data**: `data`, `datum_create`, `data_d_array`, `data_parameter`
- **Variables**: `var_general`, `var_v_array`, `var_create`
- **Beam**: `beam`, `beam_init`, `bunch_params`
- **Plotting**: `plot_list`, `plot_graph`, `plot_curve`, `plot_line`
- **Optimization**: `merit`, `constraints`, `derivative`, `optimizer`
- **Global**: `global`, `bmad_com`, `evaluate`

See `references/pipe-interface.md` for full subcommand list.

## When to Consult Reference Files

This SKILL.md covers the basics. Read a reference file when you need details beyond what's here.

**"What command do I use?" / "What's the exact syntax for ...?"**
-> Read `references/commands-reference.md` -- full syntax for all 49 commands, all `show`/`set`/`write` subcommands.

**"How do I write an init file?" / "What goes in tao.init?" / "What namelists are available?"**
-> Read `references/initialization.md` -- all CLI startup args, Fortran namelist syntax rules, every initialization namelist (`tao_start`, `tao_params`, `tao_var`, `tao_d2_data`, `tao_d1_data`, `tao_beam_init`, plotting namelists) with examples.

**"What data types exist?" / "What components does a datum have?" / "How do evaluation ranges work?"**
-> Read `references/data.md` -- full datum component list, complete data types table (90+ types with valid `data_source` and `s_offset` compatibility), merit types, evaluation points and ranges.

**"What components does a variable have?" / "How does useit_opt work?"**
-> Read `references/variables.md` -- full variable component list, `useit_opt`/`useit_plot` formulas, slave value mismatch.

**"How do expressions work?" / "What are the token types?" / "How do I specify elements?"**
-> Read `references/concepts-and-syntax.md` -- universe/lattice data model, arithmetic expressions with all intrinsic functions, all six token types (`data::`, `var::`, `lat::`, `beam::`, `ele::`, `ele_mid::`), element specification and list format, Tao-vs-Bmad parameter name mapping.

**"How do I set up plots?" / "What graph types are there?" / "How do curves work?"**
-> Read `references/plotting.md` -- plot page/region/plot/box/graph/curve hierarchy, all graph types, curve components and parameters, axis configuration.

**"How does optimization work in detail?" / "What do the merit types mean exactly?" / "What is wave analysis?"**
-> Read `references/optimization-and-wave.md` -- merit function formula, delta_D/delta_V calculation for all merit types, composite value expressions, all optimizer types and parameters, wave analysis process.

**"How do I use PyTao?" / "What pipe subcommands are available?"**
-> Read `references/pipe-interface.md` -- PyTao setup (ctypes vs pexpect), pipe output format and type codes, all ~100 pipe subcommands organized by category.

**"How does single mode work?" / "What do the keystrokes do?"**
-> Read `references/single-mode.md` -- key binding concept, complete keystroke table.

**For the most granular details** (e.g., exact behavior of a specific `show` subcommand option, or a rare initialization parameter), consult the original LaTeX manual at `docs/tao/doc/`. The structured pipe command data is at `docs/tao/doc/pipe-interface-commands.json`.
