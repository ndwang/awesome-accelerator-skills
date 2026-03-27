# Tao Reference: Plotting

Tao has a graphical display window for plotting lattice functions, machine layout, beam positions, and more. The hierarchy is: `plot_page` > `region` > `plot` > `box` > `graph` > `curve`.

## Plot Page

The `plot_page` (or plot window) is the display window where graphics are shown. Parameters can be set in an initialization file or via the `set plot_page` command:

```
set plot_page text_height = 11   ! 11 point font size
set plot_page border%x1 = 0.2    ! Set left page border to 20% of width
```

The page size is set by `plot_page%size` (width, height array) or at startup with `-geometry`:

```
tao -lattice lat.bmad -geometry 300x500
```

Use `-noplot` to start Tao without a plotting window. Display can also be controlled via `global%plot_on` in the `tao_params` namelist.

### ACC_DPI_RESOLUTION

If the screen resolution reported to Tao is incorrect (common with high-DPI displays reporting 96 dpi), set the `ACC_DPI_RESOLUTION` environment variable before running Tao:

```
export ACC_DPI_RESOLUTION=168
```

The plot page has a border; the area within the border is called the `plot area`, where regions are placed. Use `show plot -page` to view page parameters.

## Regions

Regions are invisible rectangles within the `plot area` where a plot can be placed. Each region has a name and four numbers (x1, x2, y1, y2) specifying its location, normalized to the plot area dimensions (range [0, 1]).

**Naming conventions:** `r*` (standard regions), `layout*` (layout regions), `scratch*` (scratch regions). Regions may overlap. Use `show plot` to view the region list:

```
Tao> show plot

Plot Region         <-->  Plot                 x1    x2    y1    y2     Visible
-----------               -----------------------------------------------------
layout              <-->  lat_layout          0.00  1.00  0.00  0.15         T
r13                 <-->  beta                0.00  1.00  0.72  1.00         T
r23                 <-->  dispersion          0.00  1.00  0.43  0.72         T
r33                 <-->  orbit               0.00  1.00  0.15  0.43         T
```

The `set region` command modifies region parameters:

```
set region r13 y1 = 0.8  ! Sets lower edge vertical position
```

## Plots

A plot is a collection of graphs. Plots are divided into **template** and **displayed** types:

- A **template** plot defines how a displayed plot is constructed (graph types, placement, etc.).
- When a template is **placed** in a region (via the `place` command or initialization file), its information is copied to create a **displayed** plot.
- A single template can be placed in multiple regions, and each displayed copy can be independently configured.

A displayed plot inherits the template's name. Use the region name to disambiguate. Prefix `T::` to unambiguously refer to a template plot.

```
show plot             ! Show plots associated with regions
show plot -template   ! Show template plots
place r13 orbit       ! Put orbit template into r13 region
```

Scaling: by default, `scale` ignores templates unless the `T::` prefix is used. Use the region name to scale a specific displayed plot (e.g., `scale r33 -10 10`).

## Boxes

A box is a rectangular sub-region of a plot that determines where a graph is drawn. Boxes are defined by dividing the plot into a grid and selecting a rectangle.

A box label has four numbers: `ix, iy, nx, ny` where `nx, ny` is the grid size and `ix, iy` is the position (1,1 = lower left). Different graphs can use different grids.

```
set graph myplot.g1 box = 2 1 2 2  ! Set box of graph myplot.g1
set graph myplot.g2 box = 1 1 1 2  ! Different grid for box selection
```

## Graphs

### Overview

A graph is a diagram within a plot. Most graphs have horizontal/vertical axes with curves. `floor_plan` and `lat_layout` graphs show element placement and have no curves.

Graphs are referenced as `<plot>.<graph>` (e.g., `orbit.g`). Omitting `.<graph>` selects all graphs of that plot:

```
show graph beta     ! All graphs in displayed beta plots
show graph r13.g1   ! Graph "g1" in region r13
```

### Graph Types

The `graph%type` parameter determines the type of graph:

**data** -- Plotting a dependent variable (y-axis) vs independent variable (x-axis), typically longitudinal position s. Includes data slice and parametric plotting variants.

**floor_plan** -- Physical layout of the machine. Element shapes are drawn based on a mapping table. Can include building/tunnel outlines.

**lat_layout** -- Lattice elements drawn as shapes vs longitudinal position s.

**phase_space** -- Particle positions in phase space after beam tracking.

**histogram** -- Phase space data displayed as histograms.

**dynamic_aperture** -- Results from a dynamic aperture calculation.

**key_table** -- Information about variables bound to keyboard keys (single mode).

**wave.0, wave.a, wave.b** -- Wave analysis plotting.

### Graph Axes

Data graphs have three axes: `x` (bottom), `y` (left), and `y2` (right). Axis parameters are accessed via `graph%x`, `graph%y`, `graph%y2`.

Use `scale` to set vertical axes and `x_scale` for the horizontal axis. The `y2` axis becomes independent only when a curve has `curve%use_y2 = True`.

Key axis parameters (`qp_axis_struct`):

| Parameter | Description |
|-----------|-------------|
| `label` | Axis label string |
| `min`, `max` | Axis range |
| `major_div_nominal` | Nominal number of major divisions (recommended) |
| `minor_div` | Minor divisions (0 = auto) |
| `type` | `"LINEAR"` or `"LOG"` |
| `bounds` | `"GENERAL"`, `"ZERO_AT_END"`, `"ZERO_SYMMETRIC"`, `"EXACT"` |
| `draw_label` | Whether to draw the label |
| `draw_numbers` | Whether to draw the numbers |

### Key Graph Parameters

`graph%title`, `graph%type`, `graph%x`, `graph%y`, `graph%y2` (axis params), `graph%draw_curve_legend`, `graph%curve_legend_origin`, `graph%text_legend(:)`, `graph%draw_only_good_user_data_or_vars`.

## Curves

### Overview

A curve is a data set displayed within a graph (e.g., the beta function of the model lattice). Curves have data points where symbols can be drawn and an optional smooth line. Curves are referenced as `<plot>.<graph>.<curve>`:

```
show curve beta       ! All curves in displayed beta plots
show curve r13.g1     ! Curves in graph "g1" of region r13
```

### Curve Component

The `component` parameter determines the data source variant:

```
"model"              ! Model values (default)
"design"             ! Design values
"base"               ! Base values
"meas"               ! Measured data values
"ref"                ! Reference data values
"beam_chamber_wall"  ! Beam chamber wall
```

Linear combinations are supported:

```
curve(2)%component = "model - design"   ! Plot difference
```

### Curve Data Source

The `data_source` parameter specifies the type of data:

```
"lat"               ! Computed from lattice (default)
"data"              ! From a d1_data array
"var"               ! From a v1_var array
"beam"              ! From beam tracking
"multi_turn_orbit"  ! From multi-turn tracking
```

### Curve Data Type

The `data_type` specifies what is plotted. Valid settings depend on graph type:

- **data/histogram** -- Any Tao datum type, variable, or field component (`b0_field.x`, `e0_field.y`, etc.)
- **dynamic_aperture** -- `"beam_ellipse"`, `"dynamic_aperture"`
- **phase_space** -- `"x"`, `"px"`, `"y"`, `"py"`, `"z"`, `"pz"`, `"intensity"`, `"phase_x"`, `"phase_y"`, etc.
- **floor_plan, lat_layout, key_table** -- No curves

### Curve Lines and Smooth Line Calculation

`curve%draw_line` controls whether a line is drawn. When `plot%x_axis_type` is `"s"` and component is not `"meas"` or `"ref"`, Tao calculates intermediate points for a smooth curve. Set `curve%smooth_line_calc = False` to disable (draws segments between symbol points instead). The number of evaluation points is set by `plot_page%n_curve_pts` (global) or `plot%n_curve_pts` (per-plot). To globally disable: use `-disable_smooth_line_calc` on the command line or set `global%disable_smooth_line_calc`.

### Curve Symbols

`curve%draw_symbols` controls symbol drawing. Symbol properties are set via `curve%symbol` with sub-parameters: `type` (shape: `dot`, `circle`, `square`, `plus`, `times`, `triangle`, `diamond`, `star5`, etc.), `height` (points, default 10), `color` (default `"black"`), `fill_pattern` (`solid_fill`, `no_fill`, `hatched`, `cross_hatched`). By default, symbols are drawn when `x_axis_type` is not `"s"`, `"curve"`, `"lat"`, or `"var"`.

### Key Curve Parameters

```
curve%component              ! Data component (model, design, etc.)
curve%data_source            ! Source type (lat, data, var, beam)
curve%data_type              ! What to plot (beta.x, orbit.y, etc.)
curve%draw_line              ! Draw line through data
curve%draw_symbols           ! Draw symbols at data points
curve%draw_symbol_index      ! Print index numbers beside symbols
curve%smooth_line_calc       ! Enable smooth line calculation
curve%line%width             ! Line width
curve%line%color             ! Line color
curve%line%pattern           ! solid, dashed, dash_dot, dotted, dash_dot3
curve%symbol%type            ! Symbol shape
curve%symbol%color           ! Symbol color
curve%symbol%height          ! Symbol size in points
curve%legend_text            ! Override legend text for this curve
curve%use_y2                 ! Use right-hand y2 axis
curve%ix_bunch               ! Bunch index for beam data (0 = all)
```

## Key Plotting Commands Summary

| Command | Description |
|---------|-------------|
| `place <region> <template>` | Place a template plot into a region |
| `scale <plot> <min> <max>` | Set vertical axis scale |
| `x_scale <plot> <min> <max>` | Set horizontal axis scale |
| `x_axis <plot> <type>` | Set x-axis type |
| `set plot_page <param> = <val>` | Set plot page parameters |
| `set region <name> <param> = <val>` | Set region parameters |
| `set plot <name> <param> = <val>` | Set plot parameters |
| `set graph <name> <param> = <val>` | Set graph parameters |
| `set curve <name> <param> = <val>` | Set curve parameters |
| `show plot` | Show displayed plots and regions |
| `show plot -template` | Show template plots |
| `show plot -page` | Show plot page parameters |
| `show graph <name>` | Show graph parameters |
| `show curve <name>` | Show curve parameters |
| `show curve -symbol <name>` | Show symbol (x, y, index) data |

## Colors and Line Patterns

**Colors:** `Black`, `Red`, `Green`, `Blue`, `Cyan`, `Magenta`, `Yellow`, `Orange`, `Yellow_Green`, `Light_Green`, `Navy_Blue`, `Purple`, `Reddish_Purple`, `Dark_Grey`, `Light_Grey`, `White`

**Line patterns:** `solid`, `dashed`, `dash_dot`, `dotted`, `dash_dot3`
