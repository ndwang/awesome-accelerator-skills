# Tao: operating a Bmad model

A Tao session holds lattice configurations, calculated quantities, fit targets,
adjustable parameters, and plots.

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

A **branch** is a beamline within a lattice, with its own element indices.
A single configuration can have several branches,
for example where a beamline forks. Bmad defines their physical organization;
see [Bmad concepts](bmad.md).

**Data** describe quantities to calculate or compare, such as an orbit position
or a beta function. A datum can carry calculated values and a measured or desired
value. **Variables** connect adjustable lattice attributes to the optimizer.
See [data and fitting](tao/data-and-fitting.md).

**Plots** display lattice quantities, data, variables, and particle distributions.
**Global parameters** control session behavior, including tracking mode and
optimization settings.

Official definitions: [Organization and Structure][organization], especially
`s:super.uni`, `s:universe`, and `s:lattice`.

Session files are described in [initialization](tao/initialization.md).
[Commands and scripts](tao/commands-and-scripts.md) cover inspection, model
changes, plotting, tracking, and export. [PyTao](pytao.md) provides Python access.

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
