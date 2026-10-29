# Tao: operating a Bmad model

Tao is the user program built on Bmad. It loads a lattice, calculates optics and
orbits, tracks particles, plots results, and fits model parameters to targets or
measurements. Its interactive prompt and command files use the same command
language. [PyTao](pytao.md) exposes that session to Python, so an agent can run
Tao commands and retrieve numerical results without operating a terminal prompt.

## What a Tao session contains

A **universe** holds a machine configuration and its associated data. A session
usually has one universe; multiple universes can represent different machines or
different conditions of the same machine. For example, orbit-response fitting
can use one universe per steering setting while sharing quadrupole variables.

Each universe has three lattice states:

| State | Meaning |
| --- | --- |
| `design` | The lattice originally loaded from the input files; the fixed reference |
| `model` | The working lattice changed by commands and optimizers |
| `base` | A saved comparison state, initially equal to `design` |

A **branch** is a beamline within a lattice, not another universe. Each branch
has its own element indices. A single configuration can have several branches,
for example where a beamline forks. Bmad defines their physical organization;
see [Bmad concepts](bmad.md).

**Data** describe quantities to calculate or compare, such as an orbit position
or a beta function. A datum can carry calculated values and a measured or desired
value. **Variables** connect adjustable lattice attributes to the optimizer.
Changing an element directly does not require defining a Tao variable; fitting
that attribute does. See [data and fitting](tao/data-and-fitting.md).

**Plots** display lattice quantities, data, variables, and particle distributions.
**Global parameters** control session behavior, including tracking mode and
optimization settings. These belong to the session rather than to a particular
magnet in the lattice.

Official definitions: [Organization and Structure][organization], especially
`s:super.uni`, `s:universe`, and `s:lattice`.

## Load and inspect a lattice

For the bundled [simple beamline](../assets/beamline/lattice.bmad), run this
from the directory containing `lattice.bmad`:

```sh
tao -lat lattice.bmad -noinit -noplot
```

`-lat` selects the Bmad lattice directly, `-noinit` skips `tao.init`, and
`-noplot` suppresses the native plotting window. A project with initialization
settings instead starts with `tao -init_file tao.init`.

At the Tao prompt:

```text
show lattice
show element q
show value lat::beta.a[END]
set element q k1 = 0.3
show lattice
```

The tutorial lattice has a quadrupole named `q`. `set element` changes its
strength in the model; the design lattice still contains the original strength.
Tao normally recalculates the model after a change. `show lattice` displays
optics at element exits by default. The `a` and `b` labels identify the two
transverse normal modes; their relation to horizontal and vertical motion is
described in [physics conventions](bmad/physics-conventions.md).

The same operations can be issued through an ordinary `Tao()` object; see
[PyTao](pytao.md). The Tao command semantics are the same in either interface.

## Choose a topic

| Work | Read |
| --- | --- |
| Prepare `tao.init`, load several lattices, or configure a bunch | [Initialization](tao/initialization.md) |
| Inspect optics, change attributes, select elements, write a command file, or export results | [Commands and scripts](tao/commands-and-scripts.md) |
| Define measurements or design targets, choose variables, or run a fit | [Data and fitting](tao/data-and-fitting.md) |
| Retrieve arrays, plot in Python, or automate Tao | [PyTao](pytao.md) |

Tao also provides dynamic-aperture calculations, normal-form analysis, radiation
quantities, and wave analysis for diagnosing optical errors. These capabilities
have their own settings and data types. Use the [Tao manual][manual] and the
topic-specific [official examples][examples] when extending beyond the common
tasks above.

## Official examples and reference

- [Bmad/Tao tutorial lattices][tutorial] isolate concepts such as multiple
  universes, lattice optimization, beam tracking, and Twiss correction.
- [Tao examples][examples] include more complete optics-matching, dynamic-aperture,
  collective-effects, and machine models.
- [Tao manual][manual] is the exhaustive reference. Its source chapters are
  searchable text; use the section labels supplied in these guides to locate
  definitions without reading an entire chapter.

[organization]: https://github.com/bmad-sim/bmad-ecosystem/blob/main/tao/doc/organization.tex
[manual]: https://www.classe.cornell.edu/bmad/tao.html
[tutorial]: https://github.com/bmad-sim/bmad-ecosystem/tree/main/bmad-doc/tutorial_bmad_tao/lattice_files
[examples]: https://github.com/bmad-sim/bmad-ecosystem/tree/main/bmad-doc/tao_examples
