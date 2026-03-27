# Tao Reference: Commands

Tao has two modes for entering commands. In `line mode`, Tao waits until the return key is pressed to execute a command (one command per line). In `single mode`, each keystroke is interpreted as a command. Use the `single_mode` command to switch modes.

Syntax conventions used in this reference:
```
{}        -- Identifies an optional argument
<>        -- Indicates a non-literal argument (substitute an actual value)
```

## Table of Contents

- [show](#show)
- [set](#set)
- [change](#change)
- [place](#place)
- [scale / x_scale / xy_scale](#scale--x_scale--xy_scale)
- [x_axis](#x_axis)
- [run_optimizer](#run_optimizer)
- [use / veto / restore](#use--veto--restore)
- [write](#write)
- [call](#call)
- [alias](#alias)
- [help](#help)
- [read](#read)
- [derivative](#derivative)
- [reinitialize](#reinitialize)
- [Brief Command Reference](#brief-command-reference)

---

## show

The `show` command displays information. Format:

```
show {-append <file_name>} {-noprint} {-no_err_out} <subcommand>
show {-write <file_name>} {-noprint} {-no_err_out} <subcommand>
```

The `-append` and `-write` switches write output to a file (append vs. overwrite). The `-noprint` option suppresses terminal output (useful when writing large data to a file). The `-no_err_out` switch blocks error messages from being written to the file.

When running Tao as a subprocess, use the `pipe` command instead of `show` for communication with the parent process.

### show subcommands

```
show alias                     -- Show aliases
show beam ...                  -- Show beam info
show bmad_com                  -- Old syntax for show global -bmad_com
show branch ...                -- Show lattice branch info
show building_wall             -- Show building wall info
show chromaticity ...          -- Show chromaticity, momentum compaction, phase slip
show constraints               -- Show optimization constraints
show control ...               -- Show lords and slaves of a given element
show csr_param                 -- Old syntax for show global -csr_param
show curve ...                 -- Show plot curve info
show data ...                  -- Show optimization data info
show derivative ...            -- Show d_data/d_var optimization info
show dynamic_aperture          -- Show DA info
show element ...               -- Show lattice element info
show emittance                 -- Show normal mode emittances
show field ...                 -- Show EM field
show floor_plan                -- Old syntax for show plot -floor_plan
show global ...                -- Show Tao global parameters
show graph ...                 -- Show plot graph info
show history ...               -- Show command history
show hom                       -- Show Higher Order Mode info
show internal ...              -- Used for code debugging
show key_bindings              -- Show single mode key bindings
show lattice ...               -- Lattice element-by-element table
show matrix ...                -- Show transport matrix
show merit ...                 -- Show optimization merit function
show optimizer ...             -- Show optimizer info
show particle ...              -- Show tracked particle beam info
show plot ...                  -- Show plot info
show plot_page                 -- Old syntax for show plot -page
show ptc ...                   -- Show PTC calculated parameters
show ptc_com                   -- Old syntax for show global -ptc_com
show radiation_integrals ...   -- Show synchrotron radiation integrals
show rampers                   -- Show ramper lord and slave information
show space_charge_com          -- Old syntax for show global -space_charge_com
show spin ...                  -- Show information on spin simulations
show string ...                -- Print a string
show symbolic_numbers ...      -- Show symbolic constants
show taylor_map ...            -- Show transport Taylor map
show track ...                 -- Show phase space coords, Twiss, EM field along tracked orbit
show twiss_and_orbit ...       -- Show Twiss and orbit info at given position
show universe ...              -- Show universe info
show use                       -- Show data and vars used in optimization
show value ...                 -- Show value of an expression
show variables ...             -- Show optimization variable info
show version                   -- Show Tao version
show wake_elements             -- Show wake info
show wall ...                  -- Show vacuum chamber wall info
show wave                      -- Show wave analysis info
```

Example:

```
show -write floor.dat lat -floor   -- Write floor positions to file "floor.dat"
```

---

## set

The `set` command sets values for data, variables, and many other parameters.

### set subcommands

```
set beam {n@}<parameter> = <value>
set beam_init {n@}<parameter> = <value>
set bmad_com <parameter> = <value>
set branch <branch> <parameter> = <value>
set calculate <on/off>
set curve <curve> <parameter> = <value>
set data <data_name>|<parameter> = <value>
set default <parameter> = <value>
set dynamic_aperture {n@}<parameter> = <value>
set element <element_list> <attribute> = <value>
set floor_plan <parameter> = <value>
set geodesic_lm <parameter> = <value>
set global <parameter> = <value>
set graph <graph> <parameter> = <value>
set key <key> = <command>
set lat_layout <parameter> = <value>
set lattice {n@}<destination_lat> = <source_lat>
set opti_de_param <parameter> = <value>
set particle_start {n@}<coordinate> = <value>
set plot <plot> <parameter> = <value>
set plot_page <parameter> = <value1> {<value2>}
set ptc_com <parameter> = <value>
set ran_state = <random_number_generator_state>
set region <region> <parameter> = <value>
set space_charge_com <parameter> = <value>
set symbolic_number <name> = <value>
set tune <Qa> <Qb>
set universe <what_universe> <on/off>
set variable <var_name>|<parameter> = <value>
set wave <parameter> = <value>
set z_tune <Qz>
```

Also see the `change` command, which is specialized for varying real parameters. The `show` command can display many settings that are adjustable via `set`. To apply a set to all data or variable classes use `*` in place of `<data_name>` or `<var_name>`.

### Controlling output

```
set global quiet = all        -- Suppress everything except errors
set global quiet = warnings   -- Suppress just warnings
set global quiet = off        -- No suppression
```

### Prompt color

```
set global prompt_color = <value>
```

Where `<value>` may be: `BLACK`, `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`, `GRAY`, `DEFAULT`.

---

## change

The `change` command changes element attribute values or variable values in the `model` lattice.

```
change {-update} element <element_list> <attribute> {<prefix>} <number>
change {-silent} variable <name>[<locations>] {<prefix>} <number>
change {n@}particle_start <coordinate> {<prefix>} <number>
change {-branch <branch_list>} {-listing} {-mask <veto_list>} tune {dQa} {dQb}
change {-branch <branch_list>} z_tune dQz
```

### Prefix behavior

If `<prefix>` is not present, `<number>` is added to the existing value. If present:

```
@       final_model_value = <number>                           (absolute)
d       final_model_value = design_value + <number>            (relative to design)
%       final_model_value = initial_model_value * (1 + <number> / 100)  (percentage)
```

### Coordinates for particle_start

```
x, px, y, py, z, pz, t
```

For photons additionally: `e_photon`, `field_x`, `field_y`, `phase_x`, `phase_y`. For closed lattices only `pz` is applicable. For lattices with an `e_gun`, use `t` instead of `pz`.

### Switches

- `-silent` -- Suppress printing of what variables are changed.
- `-update` -- Suppress error messages for variable slave value mismatch.
- `-mask <veto_list>` -- List of quadrupoles not to use for tune variation.
- `-listing` -- Generate list of varied quadrupoles with coefficients.

### Examples

```
change ele 3@124 x_offset 0.1          -- Offset element #124 in universe 3 by 0.1
change ele 1,3:5 x_offset 0.1          -- Offset elements 1, 3, 4, and 5 by 0.1
change ele q* k1 d 1.2e-2              -- Set k1 relative to design for elements starting with "q"
change ele quadrupole::* k1 d 1.2e-2   -- Set k1 for all quadrupole elements
change var steering[34:36] @1e-3        -- Set steering strength #34-36 to 0.001
change var steering[*] %10              -- Vary all steering strengths by 10%
change 2@particle_start x @0.001        -- Set beginning x position in universe 2 to 1 mm
change -mask Q1* tune 0 0.01            -- Change tunes without using quadrupoles named Q1*
change -branch 2@1 z_tune 0.02          -- Change z-tune of branch #1 of universe #2
```

---

## place

The `place` command associates a template plot with a region, creating a visible plot.

```
place {-no_buffer} <region> <template>
place <region> none
place * none
```

If `<region>` is `*`, all regions are selected. If `<template>` is `none`, all selected regions are cleared. A template can be placed in multiple regions (e.g., multiple orbit plots). The `-no_buffer` switch is for external plotting (e.g., with a GUI).

### Examples

```
place * none      -- Erase all plots
place top orbit   -- Place the orbit template in the top region
place top none    -- Erase any plots in the top region
```

---

## scale / x_scale / xy_scale

### scale

Scales the vertical axis of a graph or set of graphs.

```
scale {-exact} {-gang} {-include_wall} {-nogang} {-y} {-y2} {<where> {<value1> {<value2>}}}
```

- No values: autoscale (fit all data points within graph region).
- One value: scale from -`<value1>` to +`<value1>`.
- Two values: scale from `<value1>` to `<value2>`.
- `-y` / `-y2`: Scale only the right or left axis.
- `-exact`: Use exact bounds (no rounding to "nice" values).
- `-gang` / `-nogang`: Override `autoscale_gang_y` setting.
- `-include_wall`: Extend bounds to include building wall extent.

```
scale top.x -3 7    -- Scale the x graph in the top region
scale -y2 top.x     -- Scale only the y2 axis of top.x graph
scale bottom         -- Autoscale the graphs in the bottom region
```

### x_scale

Scales the horizontal axis.

```
x_scale {-exact} {-gang} {-nogang} {-include_wall} {<where> {<value1> <value2>}}
```

Where `<where>` can be `*` (all graphs), a plot name, a graph name, or `s` (only graphs using s-position). Without values, an autoscale is performed.

```
x_scale * 0 100        -- Scale all x-axes from 0 to 100
x_scale orbit -10 10   -- This "wraps around" the beginning of the lattice
x_scale s              -- Scale all graphs using x_axis = "s"
```

### xy_scale

Scales both horizontal and vertical axes. Equivalent to `x_scale` followed by `scale`.

```
xy_scale {-include_wall} {<where> {<bound1> <bound2>}}
```

```
xy_scale * -1 1       -- Scale all axes from -1 to 1
xy_scale -include     -- Autoscale all axes including building walls
```

---

## x_axis

Sets the data type used for the x-axis coordinate.

```
x_axis <where> <axis_type>
```

Possible values for `<axis_type>`:

```
index      -- Use data index
ele_index  -- Use data element index
s          -- Use longitudinal position
```

### Examples

```
x_axis * s         -- Set all plots to use longitudinal position
x_axis top index   -- Set top plot to use data index
```

---

## run_optimizer

Runs an optimizer to minimize the merit function.

```
run_optimizer {<optimizer>}
```

If `<optimizer>` is not given, the default optimizer is used. Press the period `.` key to stop the optimizer before it finishes. Valid optimizers:

```
custom        -- Used when a custom optimizer has been implemented
de            -- Differential Evolution (good for global optimizations)
geodesic_lm   -- "Geodesic" Levenburg-Marquardt (good for local optimizations)
lm            -- Levenburg-Marquardt (good for local optimizations)
lmdif         -- Levenburg-Marquardt alternative (good for local optimizations)
svd           -- SVD optimizer (good for local optimizations)
```

Use `show optimizer` to see optimizer parameters.

### Examples

```
run             -- Run the default optimizer
run de          -- Run the de optimizer
```

---

## use / veto / restore

These three commands control which data and variables participate in optimization.

### use

Un-vetoes specified data or variables and sets a veto for the rest.

```
use data <data_name>
use var <var_name>
```

```
use data orbit.x              -- Use orbit.x data in the default universe
use data *@orbit[34]          -- Use element 34 orbit data in all universes
use var quad_k1[67]           -- Use variable
use var quad_k1[30:60:10]    -- Use variables 30, 40, 50, and 60
use data *                    -- Use all data in the default universe
use data *@*                  -- Use all data in all universes
```

### veto

Vetoes data or variables (excludes them from optimization).

```
veto data <data_name> <locations>
veto var <var_name> <locations>
```

```
veto data orbit.x[23,34:56]   -- Veto orbit.x data
veto data *@orbit.*[34]       -- Veto orbit data in all universes
veto var quad_k1[67]           -- Veto variable
veto data *                    -- Veto all data
```

### restore

Cancels data or variable vetoes (un-vetoes specific items).

```
restore data <data_name> <locations>
restore var <var_name> <locations>
```

```
restore data orbit.x[23,34:56]    -- Un-veto orbit.x 23 and 34 through 56
restore data *@orbit[34]          -- Un-veto orbit data in all universes
restore var quad_k1[67]           -- Un-veto variable
```

---

## write

The `write` command creates various output files.

### write subcommands

```
write beam ...                  -- Write beam particle info to file
write blender ...               -- Write a Blender 3D script
write bmad ...                  -- Write Bmad lattice file
write bunch_comb ...            -- Write bunch combination data
write covariance_matrix ...     -- Write covariance matrix
write derivative_matrix ...     -- Write derivative matrix
write digested ...              -- Write digested lattice file
write elegant ...               -- Write Elegant lattice file
write field ...                 -- Write EM field data
write gif ...                   -- Write GIF image of plot
write hard                      -- Write hardcopy (PostScript)
write mad8 ...                  -- Write MAD8 lattice file
write madx ...                  -- Write MADX lattice file
write matrix ...                -- Write transfer matrix
write namelist ...              -- Write namelist file
write opal ...                  -- Write OPAL lattice file
write pals ...                  -- Write PALS file
write pdf ...                   -- Write PDF file of plot
write plot_commands             -- Write plot setup commands
write ps ...                    -- Write PostScript file of plot
write ptc ...                   -- Write PTC lattice file
write sad ...                   -- Write SAD lattice file
write scibmad ...               -- Write SciBmad file
write spin_mat8                 -- Write 8x8 spin/orbit matrix
write variable ...              -- Write variable values to file
write xsif ...                  -- Write XSIF lattice file
```

### Key examples

```
write beam -at *                  -- Output beam at every element
write beam -floor end             -- Output beam floor coords at element named "end"
write bmad my_lat.bmad            -- Write Bmad lattice file
write ps my_plot.ps               -- Write PostScript plot
write pdf my_plot.pdf             -- Write PDF plot
write gif my_plot.gif             -- Write GIF image
```

---

## call

Opens a command file and executes the commands in it.

```
call <filename> {<arg_list>}
call -no_calc <filename> {<arg_list>}
call -ptc <filename>
```

Up to 9 arguments may be passed. The i-th argument is substituted for the string `[[i]]` in the file. Nesting of command files is allowed with no limit. The `-no_calc` option halts all lattice and plotting calculations during execution for speed. The `-ptc` variant passes the file to PTC for processing.

If a command file calls another with a relative path, Tao looks relative to the calling file's directory. Use `$PWD/` prefix to look relative to the working directory.

### Examples

```
call -no my_cmd_file abc def     -- Run file with arg [[1]]=abc, [[2]]=def
call $PWD/../second.cmd          -- Call file relative to working directory
```

---

## alias

Defines command shortcuts, similar to Unix aliases.

```
alias {<alias_name> <string>}
```

Without arguments, prints all defined aliases. Up to 9 arguments may be substituted using `[[i]]` (required) or `[<i>]` (optional) syntax. Aliases can define multiple commands using semicolons.

### Examples

```
alias aaa show element [[1]] [[2]]   -- Alias with two required arguments
alias zzz show element [[1]] [<2>]   -- Alias with one required, one optional
alias xyzzy plot [[1]] model          -- Define xyzzy
alias                                 -- Show all aliases
xyzzy top                             -- Equivalent to "plot top model"
alias foo show uni; show top          -- Multi-command alias
```

---

## help

Gives help on Tao commands.

```
help {<command> {<subcommand>}}
```

Without arguments, lists all commands. Some commands (like `show`) have subcommand-level help.

### Examples

```
help               -- List all commands
help run           -- Help on run_optimizer
help show          -- Help on show command
help show alias    -- Help on show alias subcommand
```

The `help` command works by parsing `$TAO_DIR/doc/command-list.tex`. The environment variable `TAO_DIR` must be defined (typically set by the Bmad setup script).

---

## read

Reads a secondary lattice file to modify the `model` lattice.

```
read lattice {-silent} {-universes <universe-list>} <file_name>
```

The input file must be in Bmad standard lattice format. If `-universes` is not present, only the model lattice in the default universe is modified. The `-silent` switch suppresses error messages about differing variable slave parameter values.

Note: The number of lattice elements may not be modified by a `read` command.

### Examples

```
read lat -uni * lat.bmad       -- Modify model lattice of all universes
read lat -uni 2,3 lat.bmad    -- Modify model lattice of universes 2 and 3
```

---

## derivative

Calculates the `dModel_Data/dVar` derivative matrix needed for the `lm` optimizer.

```
derivative
```

---

## reinitialize

Reinitializes various Tao components.

```
reinitialize beam
reinitialize data
reinitialize tao {-clear} {command line optional arguments}
```

- `reinitialize beam` -- Generates a new random beam distribution at the lattice start. Also reinitializes model data.
- `reinitialize data` -- Forces recalculation of model data (usually automatic; mainly for debugging).
- `reinitialize tao` -- Reinitializes Tao entirely. Accepts the same optional arguments as the Tao command line. If `-clear` is present, all parameters reset to defaults before parsing the new arguments.

### Examples

```
reinit tao                          -- Reinitialize using previous arguments
reinit tao -init special.init       -- Reinitialize with a new init file
reinit -clear -start my_start       -- Use default init values except for start file
```

---

## Brief Command Reference

| Command | Syntax | Description |
|---------|--------|-------------|
| `clear` | `clear maps` | Clear stored spin and orbital Taylor maps from all elements |
| `clip` | `clip {-gang} {<where> {<limit1> {<limit2>}}}` | Veto data points outside given y-axis limits for plotting and optimization |
| `continue` | `continue` | Resume a suspended command file after a `pause` command |
| `create` | `create data d2_name d1_name[ix_min:ix_max] ...` | Construct new d2_data and d1_data structures for optimization |
| `cut_ring` | `cut_ring {-particle_start} {-static} {-zero}` | Toggle lattice geometry between closed and open |
| `do/enddo` | `do <var> = <l_bound>, <u_bound> {, <incr>} ... enddo` | Command file loop; use `[[<var>]]` to reference the loop variable |
| `end_file` | `end_file` | Signal end of a command file; everything after is ignored |
| `exit` | `exit` | Exit the program (same as `quit`) |
| `fixer` | `fixer activate/save/write <fixer> {<parameters>}` | Set active fixer element or transfer fixer parameters |
| `flatten` | `flatten {<optimizer>}` | Same as `run_optimizer` |
| `ls` | `ls {switches}` | List files and directories (same as `spawn ls`) |
| `pause` | `pause {<time>}` | Pause command file execution; no arg = wait for CR; negative = suspend |
| `pipe` | `pipe {-append/-write <file>} {-noprint} <subcommand> <args>` | Machine-parseable output (use instead of `show` for subprocess communication) |
| `ptc` | `ptc init` / `ptc reslice` | Initialize PTC layout or recalculate element integration parameters |
| `python` | `python ...` | Old name for `pipe` command (still accepted for compatibility) |
| `quit` | `quit` | Exit the program (same as `exit`) |
| `re_execute` | `re_execute <index>` / `re_execute <string>` | Re-run a prior command by history index or by matching string prefix |
| `single_mode` | `single_mode` | Enter single mode (each keystroke is a command; press `Z` to exit) |
| `spawn` | `spawn <shell_command>` | Pass a command to the operating system shell |
| `taper` | `taper {-universe <ix_uni>} {-except <ele_list>}` | Adjust magnet strengths to compensate for radiation sawtooth effect |
| `timer` | `timer start` / `timer read` / `timer beam` | Measure computation time or toggle beam timing mode |
| `view` | `view <universe-index>` | Shortcut for `set default universe = <n>` |
| `wave` | `wave <curve-or-data_type> {<plot_location>}` | Set data for wave analysis (orbit, beta, phase, eta, cbar, ping) |
