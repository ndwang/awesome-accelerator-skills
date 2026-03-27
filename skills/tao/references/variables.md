# Tao Reference: Variables

> See `SKILL.md` for navigation across all Tao reference files.

## Overview

Tao variables act as controllers for lattice parameters and are used primarily for optimization. A variable may control the `k1` quadrupole strength of a particular element, for example. Another use is that a block of variables can be plotted for visual inspection.

Variables are defined in the Tao initialization files (see `initialization.md`).

## Variable Organization

Blocks of variables are held in a **`v1_var`** structure. Each `v1_var` has a name used in Tao commands. For example, if `quad_k1` is the name of a `v1_var`, then `quad_k1[5]` references variable index 5.

### Indexing

Variables support comma/colon range syntax:

```
quad_k1[3:6,23]        ! Variables 3, 4, 5, 6, and 23
```

Instead of numeric indices, the associated lattice element name can be used:

```
quad_k1[q03:q06,q23]   ! Equivalent if q03 maps to index 3, etc.
```

Using element names is not valid if the same element is associated with more than one variable in a `v1_var` array (e.g., one variable for `x_offset` and another for `y_offset` of the same element).

### Wildcards

```
*                      ! All variables
quad_k1[*]|design      ! All design values of quad_k1
quad_k1[]|model        ! Empty set
quad_k1|model          ! Same as quad_k1[*]|model
```

---

## Anatomy of a Variable

A variable may control a single parameter of one element in a model lattice of a single universe, or it can simultaneously control an element attribute across multiple universes. A variable cannot control more than one attribute of one element, but it may control an overlay or group element which in turn controls many elements.

### Identification and Element Components

- **`ele_name`** -- Associated lattice element name. For controlling the starting position in an open geometry, use `particle_start`.
- **`attrib_name`** -- Name of the attribute to vary. Consult the Bmad manual for attribute names. Dependent (computed) attributes cannot be used.
- **`ix_attrib`** -- Index assigned by Bmad to the controlled attribute. Diagnostic use.
- **`s`** -- Longitudinal position of the element. May not be relevant if the variable controls multiple elements.

### Value Components

- **`model`** -- Value of the variable in the model lattice.
- **`design`** -- Value in the design lattice.
- **`base`** -- Value in the base lattice.
- **`meas`** -- Value at the time of a data measurement.
- **`ref`** -- Value at the time of a reference data measurement.
- **`correction`** -- Value determined by a fit to correct the lattice.
- **`old`** -- Scratch value.

### Optimization Components

- **`weight`** -- Weight used in the merit function.
- **`delta_merit`** -- Difference used to calculate the merit function contribution.
- **`merit`** -- Merit function term: `weight * delta^2`.
- **`merit_type`** -- `target` or `limit`.
- **`dMerit_dVar`** -- Derivative of the merit function with respect to the variable.
- **`high_lim`** -- High limit for the model value during optimization. Beyond this, the variable contributes to the merit function.
- **`low_lim`** -- Low limit for the model value during optimization.
- **`step`** -- What is considered a small change in the variable, large enough to compute derivatives.

### Key Binding Components

- **`key_bound`** -- Whether the variable is bound to a keyboard key (see `single-mode.md`).
- **`ix_key_table`** -- Index in the key table.

### Index Components

- **`ix_v1`** -- Index of this variable in the `v1_var` array. E.g., `q1_quad[10]` has `ix_v1` = 10.
- **`ix_var`** -- Index in the global variable array. Diagnostic use.
- **`ix_dvar`** -- Column in the dData_dVar derivative matrix. Diagnostic use.

### Logical Components

- **`exists`** -- Whether the variable exists. Non-existent variables serve as placeholders.
- **`good_var`** -- Set by Tao. Variables that do not affect the merit function are vetoed.
- **`good_user`** -- Set by the user via `veto`, `use`, and `restore` commands.
- **`good_opt`** -- Not modified by Tao; reserved for extension code.
- **`good_plot`** -- Set by Tao. Whether the variable point is within the horizontal plot extent.
- **`useit_opt`** -- Whether the variable is used for optimization. See formulas below.
- **`useit_plot`** -- Whether the variable is used for plotting. See formulas below.

---

## useit_opt and useit_plot Formulas

For a variable, `useit_opt` is:

```
useit_opt = exists & good_user & good_opt & good_var
```

The settings of everything except `good_user` and `good_opt` are determined by Tao.

For a variable, `useit_plot` is:

```
useit_plot = exists & good_plot & good_var &
             (good_user | graph:draw_only_good_user_data_or_vars)
```

Since `useit_plot` is set on a graph-by-graph basis, if multiple graphs use a particular variable, the final setting is from the last graph plotted.

---

## Slave Value Mismatch

A "slave value mismatch" occurs when a variable controls multiple parameters and some subset of those parameters changes value independently. For example:

- A variable controls the `k1` attribute of all elements named `Q` in the lattice. If only `Q##2` (the 2nd instance) has its `k1` changed via `set element` or `change element`, a mismatch occurs.
- A variable controls parameters in multiple universes, and only one universe is modified.
- The `read lattice` command can also cause mismatches.

Tao can fix slave value mismatches from the `set element` or `change element` commands by propagating the changed parameter to all slaves. In other cases, Tao sets all slave values to the value of the first slave.
