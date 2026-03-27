# Tao Reference: Initialization

Tao is customized for specific machines and calculations using input files. The input files tell
Tao what lattice(s) to use, what variables and data to define for optimization, how to set up
plots, and what calculations to perform.

## Table of Contents

- [Command Line Arguments](#command-line-arguments)
- [Namelist Syntax](#namelist-syntax)
- [Beginning Initialization (tao_start)](#beginning-initialization)
- [Lattice Initialization (tao_design_lattice)](#lattice-initialization)
- [Global Parameter Initialization (tao_params)](#global-parameter-initialization)
  - [tao_global_struct](#tao_global_struct)
  - [bmad_com_struct](#bmad_com_struct)
- [Beam Initialization (tao_beam_init)](#beam-initialization)
- [Variable Initialization (tao_var)](#variable-initialization)
- [Data Initialization (tao_d2_data, tao_d1_data)](#data-initialization)
- [Plotting Initialization](#plotting-initialization)
  - [Plot Page (tao_plot_page)](#plot-page)
  - [Plot Templates (tao_template_plot)](#plot-templates)
  - [Graph Templates (tao_template_graph)](#graph-templates)
- [Dynamic Aperture (tao_dynamic_aperture)](#dynamic-aperture)
- [Building Wall](#building-wall)

---

## Command Line Arguments

The syntax for starting Tao is:
```
tao {OPTIONS}
```

The optional arguments always supersede equivalent parameters set in an initialization file:

**-beam_file \<file_name\>** -- Sets the beam initialization file containing the `tao_beam_init` namelist. Overrides `beam_file` in `tao_start`.

**-beam_init_position_file \<file_name\>** -- Specifies the file containing initial particle positions. Overrides `beam_init%position_file` in the `tao_beam_init` namelist.

**-building_wall_file \<file_name\>** -- Overrides the `building_wall_file` specified in the Tao initialization file.

**-command \<command_list\>** -- List of commands to run at startup, in addition to startup file commands. Put in quotes to embed blanks or semicolons. Example:
```
tao -command "show lat 12:14; quit"
```

**-data_file \<file_name\>** -- Overrides the `data_file` specified in the Tao initialization file.

**-disable_smooth_line_calc** -- Disable computation of smooth curves used in plotting, to speed up Tao.

**-external_plotting** -- Tells Tao that plotting is done externally (e.g., by a GUI).

**-geometry \<width\>x\<height\>** -- Overrides the plot window geometry in Points. Equivalent to setting `plot_page%size`.

**-hook_init_file** -- Specifies an input file for customized versions of Tao. Default: `tao_hook.init`.

**-init_file \<file_name\>** -- Replaces the default Tao initialization file name (`tao.init`). A Tao initialization file is not strictly required; if none is used, `-lattice_file` is mandatory.

**-lattice_file \<file_name\>** -- Overrides the `design_lattice` lattice file. For multiple universes, separate file names with `|`:
```
tao -lat slac.bmad|cesr.bmad
```
For secondary lattice files, separate with commas (no spaces):
```
tao -lat primary.bmad,secondary.bmad,another_secondary.bmad
```
The file name syntax is: `{<parser>::}<lattice_file>{@<use_line1>@<use_line2>...}`.

**-log_startup** -- Creates a log file of the initialization process for debugging startup problems.

**-no_stopping** -- For debugging. Prevents Tao from stopping on fatal errors.

**-noinit** -- Suppresses use of a Tao initialization file. Requires `-lattice_file`.

**-noplot** -- Suppresses opening of the plot window.

**-nostartup** -- Suppresses the use of a startup file.

**-no_rad_int** -- Suppresses the radiation integrals calculation.

**-plot_file \<file_name\>** -- Overrides the `plot_file` specified in the Tao initialization file.

**-prompt_color** -- Sets the prompt string color to Blue.

**-quiet \<level\>** -- Suppress warning messages.

**-reverse** -- Reverses the order of lattice elements. Equivalent to `design_lattice(N)%reverse_lattice = True`.

**-rf_on** -- Leaves `rfcavity` elements on (currently the default). Use `--rf_on` to turn RF off.

**-slice_lattice \<element_list\>** -- Discard lattice elements not in the list. Overrides `design_lattice(N)%slice_lattice`.

**-start_branch_at \<element\>** -- Shift the starting point of a lattice branch. Overrides `design_lattice(N)%start_branch_at`.

**-startup_file \<file_name\>** -- Overrides the `startup_file` specified in the Tao initialization file.

**-symbol_import** -- Import symbolic constants defined in lattice files (lower cased).

**-var_file \<file_name\>** -- Overrides the `var_file` specified in the Tao initialization file.

To negate an argument, use a double-dash prefix. For example:
```
tao -noplot --noplot
```
The `-noplot` turns off plotting and `--noplot` negates it, turning plotting back on. This is useful with the `reinit tao` command.

---

## Namelist Syntax

Parameters are read using Fortran namelist input. A namelist block starts with `&` followed by the block name, and ends with `/`:
```
&namelist_block_name
  var1 = 0.123   ! exclamation marks are used for comments
  var2 = 0.456
/
```

Variables with default values can be omitted. Order is irrelevant except when the same variable appears twice (last occurrence wins). Text between namelist blocks is ignored.

### Array Setting Rules

```
&some_namelist_name
  var_array(8:11) = 34             ! Only sets var_array(8)
  var_array(8:11) = 34 34 81 81    ! OK. Sets all 4 values
  var_array(8:11) = 34, 34, 81, 81 ! OK. Same as above
  var_array(8:11) = 34, 34,        ! Lines may be continued ...
                    81, 81         !   ... like this.
  var_array(8:11) = 2*34 2*81      ! Equivalent to the preceding examples
  var_array(8:)   = 2*34 2*81      ! Also equivalent
  var_array(1:2) = 1 2 3           ! Error: Too many RHS values.
  string_arr = '1st' "2nd" '3rd'   ! Setting a string array.
/
```

The notation `n*number` is a repeat count, not multiplication. No spaces around `*`. For string input, always use quotes. Logical variables should be set to `T`/`TRUE` or `F`/`FALSE`.

**WARNING:** Namelists cannot do expression evaluation. A `/` in an expression like `3.7/148` will be taken as the namelist terminator.

---

## Beginning Initialization

The initialization starts with the root Tao initialization file (default name: `tao.init`). The first namelist read is `tao_start`:

```
&tao_start
  beam_file          = "<file_name>"  ! Default = Tao root init file.
  building_wall_file = "<file_name>"  ! No Default.
  data_file          = "<file_name>"  ! Default = Tao root init file.
  var_file           = "<file_name>"  ! Default = Tao root init file.
  plot_file          = "<file_name1> {<file_name2>} ..."
                                      ! Default = Tao root init file.
  single_mode_file   = "<file_name>"  ! Default = Tao root init file.
  startup_file       = "<file_name>"  ! Default = "tao.startup"
  hook_init_file     = "<file_name>"  ! Default = "tao_hook.init"
  init_name          = "<init_name>"  ! Default = "Tao"
/
```

File names obtained from the root initialization file are always relative to the directory where the root file lives. Command line arguments override file settings. Absolute paths are never modified.

| Namelist                | Type of Parameters     |
|-------------------------|------------------------|
| `tao_start`             | File specs             |
| `tao_design_lattice`    | Lattice files          |
| `tao_params`            | Global parameters      |
| `tao_beam_init`         | Particle beams         |
| `tao_var`               | Variables              |
| `tao_d2_data`           | Data                   |
| `tao_d1_data`           | Data                   |
| `tao_plot_page`         | Plotting               |
| `tao_template_plot`     | Plotting               |
| `tao_template_graph`    | Plotting               |
| `tao_dynamic_aperture`  | Dynamic aperture       |
| `building_wall_section` | Building walls         |

---

## Lattice Initialization

The `tao_design_lattice` namelist defines where lattice input files are:

```
&tao_design_lattice
  n_universes        = <integer>      ! Number of universes. Default = 1.
  unique_name_suffix = "<string>"
  combine_consecutive_elements_of_like_name = <logical>
  design_lattice(N) = "<lattice_file>", {"<lattice2_files>"}
  design_lattice(N)%one_turn_map_calc     = <logical>  ! Default = False
  design_lattice(N)%dynamic_aperture_calc = <logical>  ! Default = False
  design_lattice(N)%reverse_lattice       = <logical>  ! Default = False
  design_lattice(N)%slice_lattice         = "<element_list>"
  design_lattice(N)%start_branch_at       = "<element>"
/
```

The lattice file name syntax is: `{<parser>::}<lattice_file>{@<use_line1>@<use_line2>...}`. Parsers: `bmad` (default) or `digested`.

If no `design_lattice` is specified for a universe, the previous universe's settings are used.

Example:
```
&tao_design_lattice
  n_universe = 4
  design_lattice(1) = "this.lat"
  design_lattice(1)%slice_lattice = "Q1:Q2"
  design_lattice(2) = "that.lat", "floor_coords.bmad"
  design_lattice(3) = "third.lat@my_line"
  design_lattice(3)%one_turn_map_calc = True
/
```

---

## Global Parameter Initialization

Global parameters are set in the `tao_params` namelist, which groups four structures:

| Instance Name      | Structure                  | Description                |
|--------------------|----------------------------|----------------------------|
| `global`           | `tao_global_struct`        | Tao global parameters      |
| `bmad_com`         | `bmad_common_struct`       | Bmad global parameters     |
| `space_charge_com` | `space_charge_common_struct` | CSR global parameters    |
| `opti_de_param`    | `opti_de_param_struct`     | DE optimizer parameters    |

Example:
```
&tao_params
  global%optimizer = "lm"
  bmad_com%radiation_damping_on = True
/
```

### tao_global_struct

Key parameters and their defaults:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `track_type` | `"single"` | `"single"` or `"beam"` |
| `optimizer` | `"de"` | Optimizer to use (`"de"`, `"lm"`, `"svd"`, etc.) |
| `n_opti_cycles` | 20 | Number of optimization cycles |
| `n_opti_loops` | 1 | Number of optimization loops |
| `merit_stop_value` | 0 | Stop optimizer when merit falls below this |
| `dmerit_stop_value` | 0 | Stop on fractional merit change below this |
| `lmdif_eps` | 1e-12 | Tolerance for lmdif optimizer |
| `svd_cutoff` | 1e-5 | SVD singular value cutoff |
| `random_seed` | -1 | -1 = system clock |
| `random_engine` | `"pseudo"` | `"pseudo"` or `"quasi"` |
| `random_gauss_converter` | `"exact"` | `"exact"` or `"limited"` |
| `random_sigma_cutoff` | -1 | Cutoff in sigmas |
| `phase_units` | `"radians"` | Phase units on output |
| `rf_on` | F | RF cavities on? |
| `lattice_calc_on` | T | Turn on/off beam and single particle calculations |
| `plot_on` | T | Do plotting? |
| `var_limits_on` | T | Respect variable limits? |
| `derivative_recalc` | T | Recalc derivatives before each optimizer loop? |
| `derivative_uses_design` | F | Use design lattice for derivative matrix? |
| `disable_smooth_line_calc` | F | Disable smooth line calc for plotting? |
| `beam_dead_cutoff` | 0.99 | Dead particle cutoff for stopping beam tracking |
| `prompt_string` | `"Tao"` | Command prompt string |
| `var_out_file` | `"var#.out"` | Output file for optimizer variable values |

### bmad_com_struct

Key Bmad global parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `radiation_damping_on` | F | Damping toggle |
| `radiation_fluctuations_on` | F | Fluctuations toggle |
| `spin_tracking_on` | F | Spin tracking? |
| `sr_wakes_on` | T | Short range wakefields? |
| `lr_wakes_on` | T | Long range wakefields? |
| `csr_and_space_charge_on` | F | Space charge switch |
| `taylor_order` | 3 | Taylor map order |
| `aperture_limit_on` | T | Use apertures in tracking? |
| `max_aperture_limit` | 1e3 | Maximum aperture limit (m) |
| `rel_tol_tracking` | 1e-8 | Relative tracking tolerance |
| `abs_tol_tracking` | 1e-10 | Absolute tracking tolerance |

---

## Beam Initialization

Beam tracking is enabled by setting `global%track_type = "beam"` in `tao_params`. Beam parameters are set in the `tao_beam_init` namelist:

```
&tao_beam_init
  ix_universe               = <integer>     ! Universe to apply to.
  always_reinit             = <logical>     ! Always reinit distribution?
  saved_at                  = "<ele_list>"  ! Elements to save beam info at.
  dump_file                 = "<file_name>" ! File for saving beam info.
  dump_at                   = "<ele_list>"  ! Save beam info at these elements.
  track_start               = "<ele_id>"    ! Beam tracking start element.
  track_end                 = "<ele_id>"    ! Beam tracking end element.
  comb_ds_save              = <real>        ! Step size for beam parameter evaluation.
  beam_init%position_file   = <string>      ! Beam position init file.
  beam_init%distribution_type(3) = "<type>" ! "RAN_GAUSS" (default), "ELLIPSE",
                                            !   "KV", or "GRID".
  beam_init%a_norm_emit     = <real>        ! A-mode normalized emittance
  beam_init%b_norm_emit     = <real>        ! B-mode normalized emittance
  beam_init%a_emit          = <real>        ! A-mode geometric emittance
  beam_init%b_emit          = <real>        ! B-mode geometric emittance
  beam_init%dPz_dZ          = <real>        ! Energy-Z correlation
  beam_init%center          = <real>*6      ! Bunch center offset (Bmad coords)
  beam_init%sig_pz          = <real>        ! Energy spread sigma in dE/E0
  beam_init%sig_z           = <real>        ! Z sigma in meters
  beam_init%n_bunch         = <integer>     ! Number of bunches
  beam_init%n_particle      = <real>        ! Number of particles per bunch
  beam_init%bunch_charge    = <real>        ! Charge per bunch (Coulombs)
  beam_init%spin(3)         = <real>*3      ! (x, y, z) spin components
  beam_init%use_t_coords    = <logical>     ! Use time coords (for e_guns)?
/
```

Multiple `tao_beam_init` namelists may exist for different universes (set via `ix_universe`). If `ix_universe` is -1 or absent, parameters apply to all universes.

---

## Variable Initialization

Variables are initialized using the `tao_var` namelist. One block is needed per variable array:

```
&tao_var
  v1_var%name          = "<array_name>"  ! Variable array name.
  default_universe     = "<integer>"     ! Universe. "gang" or "clone" modes.
  default_attribute    = "<attrib_name>" ! Attribute to control.
  default_weight       = <real>          ! Merit function weight. Default: 0.
  default_step         = <real>          ! Small step value. Default: 0.
  default_merit_type   = "<merit_type>"  ! Default = "limit"
  default_low_lim      = <real>          ! Lower limit. Default: -1e30
  default_high_lim     = <real>          ! Upper limit. Default: 1e30
  default_key_delta    = <real>          ! Change when key is pressed.
  default_key_bound    = <logical>       ! Variable bound to key?
  default_good_user    = <logical>       ! Vary for optimization? Default: T
  ix_min_var           = <integer>       ! Minimum array index.
  ix_max_var           = <integer>       ! Maximum array index.
  search_for_lat_eles  = "<ele_list>"    ! Find elements by name.
  use_same_lat_eles_as = "<d1_name>"     ! Reuse a previous element list.
  var(N)%ele_name      = "<ele_name>"    ! Element to be controlled.
  var(N)%attribute     = "<attrib_name>" ! Attribute to be controlled.
  var(N)%universe      = "<uni_list>"    ! Universe. "*" => All.
  var(N)%weight        = <real>          ! Merit function weight.
  var(N)%step          = <real>          ! Small step size.
  var(N)%low_lim       = <real>          ! Lower variable value limit.
  var(N)%high_lim      = <real>          ! Upper variable value limit.
  var(N)%merit_type    = "<merit_type>"  ! "limit" (default) or "target".
  var(N)%good_user     = <logical>       ! Good optimization variable?
  var(N)%key_bound     = <logical>       ! Variable bound to a key.
  var(N)%key_delta     = <real>          ! Change when key is pressed.
/
```

Example:
```
&tao_var
  v1_var%name        = "v_steer"
  default_universe   = "clone 2,3"
  default_attribute  = "vkick"
  default_weight     = 1e3
  default_step       = 1e-5
  var(0:99)%ele_name = "v00w", "v01w", "v02w", "    ", "v04w", ...
  var(2)%attribute   = "hkick"     ! Override default
/
```

The `default_universe` can be set to `"gang"` (controls all universes simultaneously, the default) or `"clone"` (duplicates the variable array for each universe). Blank `var(N)%ele_name` entries indicate non-existent variables. The `search_for_lat_eles` parameter can be used to find elements by name pattern (e.g., `"sbend::b*"`).

---

## Data Initialization

Data is initialized using paired `tao_d2_data` and `tao_d1_data` namelists.

### tao_d2_data Namelist

```
&tao_d2_data
  d2_data%name       = "<d2_name>"        ! Name for the d2_data structure.
  universe           = "<list>"           ! Universes. "*" => all (default).
  default_merit_type = "<merit_type>"     ! "target", "max", "min", etc.
  n_d1_data          = <integer>          ! Number of associated d1_data arrays.
/
```

Merit type options: `"target"`, `"max"`, `"min"`, `"abs_max"`, `"abs_min"`, `"max-min"`, `"average"`, `"integral"`.

### tao_d1_data Namelist

Each `tao_d1_data` must follow its associated `tao_d2_data`:

```
&tao_d1_data
  ix_d1_data             = <integer>           ! d1_data index (1, 2, ...)
  d1_data%name           = "<d1_name>"         ! d1_data name.
  default_data_type      = <type_name>         ! E.g., orbit.x, e_tot, etc.
  default_weight         = <real>              ! Merit function weight. Default: 0.
  default_data_source    = "<source>"          ! "lat" (default), "beam", "data", "var"
  default_merit_type     = "<merit_type>"      ! Sets default for datums.
  ix_min_data            = <integer>           ! Minimum array index.
  ix_max_data            = <integer>           ! Maximum array index.
  search_for_lat_eles    = "<element_list>"    ! Find elements by name.
  use_same_lat_eles_as   = "<d1_name>"         ! Reuse previous element list.
  datum(N)%data_type      = "<type_name>"      ! E.g., "orbit.x"
  datum(N)%data_source    = "<source>"         ! "lat", "beam", "data", "var"
  datum(N)%ele_name       = "<ele_name>"       ! Evaluation element name.
  datum(N)%ele_start_name = "<ele_start_name>" ! Start element (for ranges).
  datum(N)%ele_ref_name   = "<ele_ref_name>"   ! Reference element.
  datum(N)%merit_type     = "<merit_type>"
  datum(N)%meas           = <real>             ! "Measured" value.
  datum(N)%weight         = <real>             ! Merit function weight.
  datum(N)%good_user      = <logical>          ! Use for optimization? Default: T
  datum(N)%eval_point     = "<where>"          ! "beginning", "center", "end" (default)
  datum(N)%ix_bunch       = <integer>          ! Bunch index. 0 = all bunches.
/
```

If `datum(N)%data_type` is not set and `default_data_type` is not specified, the type is constructed from the `d2_data` and `d1_data` names (e.g., `d2_data%name = "orbit"` and `d1_data%name = "x"` gives `"orbit.x"`).

### Data Example (component-by-component format)

```
&tao_d2_data
  d2_data%name = "orbit"
  universe     = "1,3:5"
  n_d1_data    = 2
/

&tao_d1_data
  ix_d1_data        = 1
  d1_data%name      = "x"
  default_weight    = 1e6
  ix_min_data       = 0
  ix_max_data       = 99
  datum(0:)%ele_name = "DET_00W", " ", "DET_02W", ...
  datum(0:)%weight   = 0.23,      0,   0.45, ...
/
```

### Data Example (datum-by-datum format)

```
&tao_d1_data
  ix_d1_data        = 1
  d1_data%name      = "t"
  !           data_      ele_ref  ele_start ele       merit    meas   weight good
  !           type       name     name      name      type     value         user
  datum( 1) = "beta.a"   "S:2.3"  ""       "Q16_1"   "max"     30    0.1     T
  datum( 2) = "eta.x"    ""       "B22"    "Q16##2"  "max"     30    0.1     T
  datum( 3) = "floor.x"  ""       ""       "end"     "target"   3    0.01    T
/
```

---

## Plotting Initialization

Plotting is defined in the file specified by `plot_file` in the `tao_start` namelist.

### Plot Page

The `tao_plot_page` namelist sets plot page parameters, regions, and initial plot placement:

```
&tao_plot_page
  plot_page%title                    = "<string>", <x>, <y>, "<units>", "<justify>"
  plot_page%subtitle                 = "<string>", <x>, <y>, "<units>", "<justify>"
  plot_page%plot_display_type        = "<string>"  ! "X", "TK", or "QT"
  plot_page%size                     = <x_size>, <y_size>  ! Window size (Points)
  plot_page%border                   = <x1>, <x2>, <y1>, <y2>, "<units>"
  plot_page%text_height              = <real>   ! Height in Points. Default = 12
  plot_page%main_title_text_scale    = <real>   ! Default = 1.3
  plot_page%graph_title_text_scale   = <real>   ! Default = 1.1
  plot_page%axis_number_text_scale   = <real>   ! Default = 0.9
  plot_page%axis_label_text_scale    = <real>   ! Default = 1.0
  plot_page%legend_text_scale        = <real>   ! Default = 0.8
  plot_page%n_curve_pts              = <int>    ! Default = 401
  plot_page%delete_overlapping_plots = <T/F>    ! Default = T
  include_default_plots              = <T/F>    ! Default = T
  region(N) = "<region_name>" <x1>, <x2>, <y1>, <y2>
  place(N)  = "<region_name>", "<template_name>"
  default_plot%...
  default_graph%...
/
```

Example:
```
&tao_plot_page
  plot_page%title = "CESR Lattice", 0.5, 0.996, "%PAGE", "CC"
  plot_page%size        = 700, 800
  plot_page%text_height = 12.0
  region(1) = "top"    0.0, 1.0, 0.5, 1.0
  region(2) = "bottom" 0.0, 1.0, 0.0, 0.5
  place(1)  = "top",    "orbit"
  place(2)  = "bottom", "phase"
/
```

### Plot Templates

The `tao_template_plot` namelist defines a plot template:

```
&tao_template_plot
  plot%name            = "<plot_name>"
  plot%x_axis_type     = "<type>"       ! "index", "ele_index", "s", "lat", "var", etc.
  plot%autoscale_gang_x = <logical>     ! Default: True
  plot%autoscale_gang_y = <logical>     ! Default: True
  plot%autoscale_x     = <logical>      ! Default: False
  plot%autoscale_y     = <logical>      ! Default: False
  plot%n_curve_pts     = <integer>      ! Overrides plot_page%n_curve_pts.
  plot%n_graph         = <n_graphs>     ! Number of associated graphs.
  default_graph%...
  default_curve%...
/
```

The `x_axis_type` options are: `"index"`, `"ele_index"`, `"s"`, `"data"`, `"lat"`, `"var"`, `"phase_space"`, `"floor"`, `"none"`.

### Graph Templates

Each graph associated with a plot needs a `tao_template_graph` namelist placed after the `tao_template_plot`:

```
&tao_template_graph
  graph_index              = <integer>          ! 1 = first graph, etc.
  graph%name               = "<string>"         ! Default: "g<n>"
  graph%type               = "<string>"         ! "data", "floor_plan", etc.
  graph%box                = <ix>, <iy>, <ix_tot>, <iy_tot>
  graph%title              = "<string>"
  graph%margin             = <x1>, <x2>, <y1>, <y2>, "<Units>"
  graph%x                  = <qp_axis_struct>   ! Horizontal axis
  graph%y                  = <qp_axis_struct>   ! Left vertical axis
  graph%y2                 = <qp_axis_struct>   ! Right vertical axis
  graph%y2_mirrors_y       = <logical>          ! Default = T
  graph%clip               = <logical>          ! Default = T
  graph%ix_universe        = <integer>          ! -1 => default universe
  graph%n_curve            = <integer>          ! Limit number of curves
  curve(N)%data_type       = "<string>"         ! E.g., "orbit.x"
  curve(N)%data_source     = "<string>"         ! Data source
  curve(N)%component       = "<string>"         ! E.g., "model - design"
  curve(N)%y_axis_scale_factor = <factor>
  curve(N)%use_y2          = <logical>          ! Use right-axis scale?
  curve(N)%draw_line       = <logical>          ! Connect data with lines?
  curve(N)%draw_symbols    = <logical>          ! Draw data symbols?
  curve(N)%ix_universe     = <integer>          ! -1 => default
  curve(N)%line            = <qp_line_struct>   ! Line spec
  curve(N)%symbol          = <qp_symbol_struct> ! Symbol spec
/
```

Example:
```
&tao_template_graph
  graph_index               = 1
  graph%name                = "x"
  graph%type                = "data"
  graph%box                 = 1, 1, 1, 2
  graph%title               = "Horizontal Orbit (mm)"
  graph%margin              =  60, 200, 30, 30, "POINTS"
  graph%y%label             = "X"
  curve(1)%component        = "model - design"
  curve(1)%data_source      = "data"
  curve(1)%data_type        = "orbit.x"
  curve(1)%y_axis_scale_factor = 1000
/
```

---

## Dynamic Aperture

The dynamic aperture calculation finds the stability region in phase space for a storage ring. Enable it by setting `design_lattice(N)%dynamic_aperture_calc = T` in the `tao_design_lattice` namelist.

Parameters are set in the `tao_dynamic_aperture` namelist:

```
&tao_dynamic_aperture
  ix_universe            = -1        ! -1 = all universes
  pz                     = 0, 0.01   ! List of pz values for scans
  a_emit                 = 1e-11     ! A-mode emittance (for data calc)
  b_emit                 = 1e-13     ! B-mode emittance (for data calc)
  ellipse_scale          = 10        ! Beam ellipse scale (sigmas)
  da_param%start_ele     = ''        ! Start element for tracking
  da_param%n_angle       = 21        ! Number of angles per scan
  da_param%min_angle     = 0         ! Starting scan angle (rad)
  da_param%max_angle     = 3.1416    ! Ending scan angle (rad)
  da_param%n_turn        = 2000      ! Number of turns for stability
  da_param%rel_accuracy  = 1e-2      ! Relative accuracy of boundary
  da_param%abs_accuracy  = 1e-5      ! Absolute accuracy (meters)
  da_param%x_init        = 1e-3      ! Initial horizontal aperture estimate
  da_param%y_init        = 1e-3      ! Initial vertical aperture estimate
/
```

A particle is considered stable if it survives the specified number of turns. The boundary between stable and unstable motion is found iteratively along rays emanating from the closed orbit. Multiple `tao_dynamic_aperture` namelists may be present for different universes.

---

## Building Wall

A two-dimensional cross-section of the building can be defined for floor plan plotting or machine-to-building optimization. Wall sections are defined in the file specified by `building_wall_file` using `building_wall_section` namelists:

```
&building_wall_section
  name       = "<string>"         ! Optional name for shape matching
  constraint = "<type>"           ! "right_side", "left_side", or "none" (default)
  point(1) = <z1>, <x1>
  point(2) = <z2>, <x2>, {<r2>}  ! Optional radius for circular arc
  ...
  point(N) = <zN>, <xN>, {<rN>}
/
```

Points are in the Bmad global (Z, X) coordinate system. A non-zero radius between adjacent points creates a circular arc segment; otherwise the segment is a straight line.
