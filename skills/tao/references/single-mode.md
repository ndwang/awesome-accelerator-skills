# Tao Reference: Single Mode

Tao has two modes for entering commands. In Single Mode, each keystroke represents a command -- the user does not have to press the return key to signal the end of a command (with a few exceptions noted below). Conversely, in Line Mode, Tao waits until the return key is pressed to execute a command, where a command consists of a single line of input. Single Mode is useful for quickly varying parameters to see how they affect a lattice, but the number of available commands is limited.

From Line Mode, use the `single_mode` command to enter Single Mode. To return to Line Mode, type `Z`.

## Key Bindings

The main purpose of Single Mode is to associate certain keyboard keys with certain variables so that pressing these keys will change the associated model value of the variable. This is called a key binding.

Key bindings are established in a startup file by setting the `var(i)%key_bound` and `var(i)%key_delta` parameters. After startup, variables can be associated with keyboard keys using the `set variable` command.

### Variable Banks

The variables are divided into banks of 10. The 0th bank uses the first ten variables that have their `key_bound` attribute set to True. The 1st bank uses the next ten, and so on. At any one time, only one bank is active. To see the status of the current bank, a `key_table` plot can be set up.

Initially the 0th bank is active. The left arrow and right arrow keys are used to decrease or increase the bank number. Additionally the `<` and `>` keys can be used to change the deltas for all variables.

### Variable Key Map

The relationship between key presses and variable changes is shown below. Each variable has a pair of keys: one on the number row to increment and one on the letter row (directly below) to decrement. The change is in multiples of the variable's `step` value.

```
                 Change by factor of:
     Variable    -10  -1    1     10
   ----------    ---  ---  ---  -------
    1 + 10*ib     Q    q    1   shift-1   ("!")
    2 + 10*ib     W    w    2   shift-2   ("@")
    3 + 10*ib     E    e    3   shift-3   ("#")
    4 + 10*ib     R    r    4   shift-4   ("$")
    5 + 10*ib     T    t    5   shift-5   ("%")
    6 + 10*ib     Y    y    6   shift-6   ("^")
    7 + 10*ib     U    u    7   shift-7   ("&")
    8 + 10*ib     I    i    8   shift-8   ("*")
    9 + 10*ib     O    o    9   shift-9   ("(")
   10 + 10*ib     P    p    0   shift-0   (")")
```

In the above table, `ib` is the bank number (0 for the 0th bank, etc.). In Line Mode, the command `show key_bindings` may be used to show the entire set of bound keys.

## List of Key Strokes

In the following list, certain commands use multiple key strokes. For example, the `/v` command is invoked by first pressing the `/` key followed by the `v` key. `a <left_arrow>` represents pressing the `a` key followed by the left-arrow key.

Custom commands can be associated with any key using the `set key` command. Example:

```
set key h = veto var *  ! This sets the "h" key to the command "veto var *"
```

### Variable Adjustment Keys

| Key | Action |
|-----|--------|
| `1` through `9`, `0` | Change variable 1-10 of current bank by +1 delta |
| `q`,`w`,`e`,`r`,`t`,`y`,`u`,`i`,`o`,`p` | Change variable 1-10 of current bank by -1 delta |
| `!`,`@`,`#`,`$`,`%`,`^`,`&`,`*`,`(`,`)` (Shift+number) | Change variable 1-10 of current bank by +10 delta |
| `Q`,`W`,`E`,`R`,`T`,`Y`,`U`,`I`,`O`,`P` (Shift+letter) | Change variable 1-10 of current bank by -10 delta |

### Delta and Bank Control Keys

| Key | Action |
|-----|--------|
| `<` | Reduce all variable deltas by a factor of 2 |
| `>` | Increase all variable deltas by a factor of 2 |
| `/ <up_arrow>` | Increase all key deltas by a factor of 10 |
| `/ <down_arrow>` | Decrease all key deltas by a factor of 10 |
| `<left_arrow>` | Shift the active key bank down by 1 |
| `<right_arrow>` | Shift the active key bank up by 1 |

### Plot Navigation Keys

| Key | Action |
|-----|--------|
| `a <left_arrow>` | Pan plots left by half the plot width |
| `a <right_arrow>` | Pan plots right by half the plot width |
| `a <up_arrow>` | Pan plots up by half the plot height |
| `a <down_arrow>` | Pan plots down by half the plot height |
| `s <left_arrow>` | Scale x-axis of plots by a factor of 2.0 |
| `s <right_arrow>` | Scale x-axis of plots by a factor of 0.5 |
| `s <up_arrow>` | Scale y-axis of plots by a factor of 2.0 |
| `s <down_arrow>` | Scale y-axis of plots by a factor of 0.5 |
| `z <left_arrow>` | Zoom x-axis of plots by a factor of 2.0 |
| `z <right_arrow>` | Zoom x-axis of plots by a factor of 0.5 |
| `z <up_arrow>` | Zoom y-axis of plots by a factor of 2.0 |
| `z <down_arrow>` | Zoom y-axis of plots by a factor of 0.5 |

### Display and Information Keys

| Key | Action |
|-----|--------|
| `?` | Display a short help message |
| `c` | Show constraints |
| `v` | Show Bmad variable values in Bmad lattice format (equivalent to `show vars -bmad` in Line Mode) |
| `V` | Same as `v` but only shows variables currently enabled for optimization (equivalent to `show vars -bmad -good`) |
| `/v` | Write variable values to the default output file in Bmad lattice format. The output file name is set by `global%var_out` |
| `/l` | Print a list of the lattice elements with Twiss parameters |
| `/e <Index or Name>` | Print info on a lattice element. Prepend with `n@` to specify a particular lattice index |
| `/b` | Switch the default lattice branch |
| `/u <Universe Index>` | Switch the default universe |

### Axis and Scale Commands

| Key | Action |
|-----|--------|
| `/x <min> <max>` | Set horizontal scale min and max for all plots. If omitted, scale includes entire lattice |
| `/y <min> <max>` | Set y-axis min and max for all plots. If omitted, autoscale is performed |

### Value Setting Keys

| Key | Action |
|-----|--------|
| `=v <digit> <value>` | Set a variable value. `<digit>` is 0-9 corresponding to a variable of the current bank |
| `= <right_arrow>` | Save current variable values to saved (`value0`) values. Saved values are initially set to startup values. Reading a TOAD input file will reset saved values |
| `= <left_arrow>` | Paste saved (`value0`) values back to the variable values |

### Other Keys

| Key | Action |
|-----|--------|
| `g` | Run the default optimizer. The optimizer runs until you type `.` (period). During optimization, variable values are periodically written to files named `tao_opt_vars#.dat` where `#` is the universe number |
| `Z` | Return to Line Mode |
| `-p` | Toggle plotting on/off. Initial state is determined by `plot%enable` |
| `' <command>` | Accept a Line Mode command |
| `<CR>` (Enter) | Do nothing but replot |
