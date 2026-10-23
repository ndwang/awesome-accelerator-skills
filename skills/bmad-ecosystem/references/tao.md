# Tao: initialization, inspection, and fitting

Use Tao for interactive calculations and machine-model manipulation. Use [bmad.md](bmad.md) for the underlying physics and lattice language, and [pytao.md](pytao.md) for Python automation. Check installed command help before applying syntax from the pinned sources below.

## Load a reproducible session

Prefer the user's existing initialization file and directory layout. Inspect `tao.init`, its named lattice/data/variable files, and any startup command files. Loading an initialization file can execute startup commands; keep those as part of the reproduction.

For a separate small example, copy [assets/fodo](../assets/fodo/tao.init) to a working directory, enter that directory, and run:

```sh
tao -init_file tao.init -noplot
```

The `-noplot` option suppresses the native plot window. If using a lattice directly, the installed help documents the `-lattice_file` and `-noinit` options. A `tao_start` namelist's `lattice_file` points to the file containing the `tao_design_lattice` namelist; `design_lattice(N)` within that namelist selects the Bmad lattice for universe `N`. Preserve this distinction when repairing initialization. [Initialization source][initialization]

Start by inspecting:

```text
show version
show global
show lattice
help show element
help set element
```

`show version` relies on installation metadata including `TAO_DIR`; a missing version report can be an environment issue. Preserve the startup output and the selected executable path when recording a reproduction. [Command source][commands]

## Identify the state being read or changed

| Concept | Meaning and practical consequence |
| --- | --- |
| Universe | One machine configuration with its lattices and associated data; make the universe explicit for multi-configuration work. |
| Branch | A beamline within a lattice; element indices are branch-specific. |
| Design | Fixed lattice loaded from the lattice description. |
| Model | Working lattice normally modified by Tao commands and optimizers. |
| Base | Reference snapshot used for comparisons; initially equal to design and explicitly replaceable. |

All three lattice states start identically. Query the intended state consistently; a comparison against `base` is meaningful only if its snapshot is known. Read [organization.tex][organization], sections `s:universe` and `s:lattice`, for the definitions.

Use explicit element identifiers where ambiguity matters. `2@1>>QF` selects `QF` in universe 2, branch 1; `QF##2` selects the second occurrence in the relevant branch. Inspect the resolved element before changing it. Tao command words are case sensitive; Bmad element names within commands are generally case insensitive. [Syntax source][syntax]

## Change one quantity and verify it

For an existing element named `QF`, first inspect its attributes:

```text
show element QF
set element QF k1 = 1.2
show element QF
show lattice
```

Treat the value as an absolute replacement. Read `help change element` if the task calls for a relative change. Confirm that a wildcard, repeated name, or lord/slave relationship has not changed additional elements. [Command source][commands]

Tao normally recalculates the affected lattice after a command. If batching changes with `set global lattice_calc_on = F`, record the previous flag, re-enable calculation before reading results, and restore the original setting on all exit paths. Distinguish a current calculated result from stale output while calculation was disabled. Apply the same discipline to plot and tracking-mode flags. [Organization][organization] and [initialization][initialization]

## Configure fitting deliberately

Read [data.tex][data], [variables.tex][variables], and [optimization.tex][optimization] before generating a fit setup.

1. Define the physical knobs and identify the lattice attributes they control, including any sharing across universes.
2. Define the observables, target values, units, weights, and active constraints. Inspect which variables and data are actually enabled for optimization.
3. Set meaningful bounds and a starting point. Verify that initial calculated data are valid and that a small knob perturbation changes the intended observable.
4. Run a short fit and inspect convergence, residuals, limits, and lattice stability before extending it.
5. Compare the final model to the initial snapshot. Export the resulting settings and reload them in a fresh session to verify reproducibility.

Treat invalid optics, particle loss, or an unstable lattice as failed evaluations with an explicit policy. Do not replace failed points with zero-valued observations or label an optimizer termination as proof of a good physical solution.

## Use the right output interface

Use `show` commands to inspect a session. For programmatic extraction, prefer PyTao's parsed methods or Tao's documented `pipe` interface. The common parameter-list form is `name;type;can_vary;value...`, but individual pipe commands have their own schemas, including arrays and tables. Read the exact subcommand definition before parsing it. Pipe output is intended to be more stable than human-formatted `show` output, but it remains version-sensitive. [Pipe interface][pipe] and [pipe commands][pipe_commands]

For a failure, capture the exact initialization, command, selected universe/branch/state, and full diagnostic. Resolve the first causal error, then reload and rerun the smallest relevant calculation. Keep plotting failures separate from numerical results when diagnosing a headless environment.

[initialization]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/tao/doc/initialization.tex
[commands]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/tao/doc/command-list.tex
[organization]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/tao/doc/organization.tex
[syntax]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/tao/doc/syntax.tex
[data]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/tao/doc/data.tex
[variables]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/tao/doc/variables.tex
[optimization]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/tao/doc/optimization.tex
[pipe]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/tao/doc/pipe-interface.tex
[pipe_commands]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/tao/doc/pipe-interface-commands.tex
