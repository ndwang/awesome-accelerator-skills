---
name: bmad-ecosystem
description: Install Bmad, Tao, and PyTao, write and understand Bmad accelerator lattices, prepare Tao initialization files and command scripts, and use PyTao from Python. Use for Bmad physics conventions and element definitions, Tao optics/tracking/fitting tasks, and Python access to a Tao model.
license: GPL-3.0-only
metadata:
  author: Ningdong Wang
  version: "2.0.0"
---

# Bmad, Tao, and PyTao

## How the pieces fit together

**Bmad** is the accelerator physics library and lattice language. A Bmad lattice
describes the particle and reference energy, beamline elements, their arrangement,
and the physical models used for calculations.

**Tao** is a user program built on Bmad. It loads lattices, calculates optics,
tracks particles, plots results, and fits adjustable parameters to target data.
Its initialization files establish a session; its commands inspect and change
that session.

**PyTao** exposes a Tao session to Python through the Tao shared library. A
`Tao` object loads a model, runs commands, and returns calculated quantities
for analysis and plotting.

| File | What it describes |
| --- | --- |
| `.bmad` | The lattice: elements, lines, reference quantities, and physics settings |
| `tao.init` and related initialization files | Tao namelists: lattices to load, data, variables, beam and plot setup |
| Tao command files, often `.tao` | Commands to execute in a Tao session, including aliases and parameterized scripts |
| Python scripts or notebooks | PyTao calls, numerical analysis, automation, and Python plotting |

## Read for the task

The three guides introduce the concepts and capabilities of each layer. Go
directly to a topic reference when the task is already specific.

| Task | Reference |
| --- | --- |
| Install Bmad/Tao and PyTao or resolve library-loading problems | [Installation](references/installation.md) |
| Understand a lattice or choose a Bmad capability | [Bmad concepts](references/bmad.md) |
| Write definitions, expressions, lines, or includes | [Lattice syntax](references/bmad/lattice-syntax.md) |
| Choose an element and understand its defining attributes | [Elements](references/bmad/elements.md) |
| Interpret coordinates, units, or reference quantities | [Physics conventions](references/bmad/physics-conventions.md) |
| Understand or build a controller | [Controllers](references/bmad/controllers.md) |
| Understand Tao's session and lattice states | [Tao concepts](references/tao.md) |
| Prepare `tao.init`, load lattices, or configure universes | [Initialization](references/tao/initialization.md) |
| Find commands or write a Tao script | [Commands and scripts](references/tao/commands-and-scripts.md) |
| Define data and variables or fit optics | [Data and fitting](references/tao/data-and-fitting.md) |
| Load, query, and analyze a model in Python | [PyTao](references/pytao.md) |

## Examples and detailed documentation

The guides pair short explanations and common syntax with links to official
manual sections and curated examples. Use those sections for complete attribute
lists, less common options, and detailed physics. Section names and search labels
help locate the relevant part of a large manual source file. For version-specific
interfaces, use the documentation corresponding to the installed software.

- **First lattice:** [lattice.bmad](assets/beamline/lattice.bmad), the official
  tutorial's small open electron beamline. It shows entrance optics, reference
  energy, a drift, a bend, a quadrupole, and a line. See
  [Bmad](references/bmad.md) for its structure and [PyTao](references/pytao.md)
  for loading a lattice from Python.
- **Optics fitting:** the official tutorial's
  [lattice](assets/matching/lat.bmad), [initialization](assets/matching/tao.init),
  and [startup commands](assets/matching/setup.tao). The
  [fitting guide](references/tao/data-and-fitting.md) explains the data targets
  and adjustable quadrupole strengths. Keep these three files together.
- **Python examples:** the [PyTao guide](references/pytao.md) uses the bundled
  lattices for model access, fitting, and plotting, with upstream notebooks
  as further reference.

Official entry points: [Bmad manual](https://www.classe.cornell.edu/bmad/manual.html),
[Tao](https://www.classe.cornell.edu/bmad/tao.html),
[Bmad/Tao tutorial examples](https://github.com/bmad-sim/bmad-ecosystem/tree/main/bmad-doc),
and [PyTao documentation](https://bmad-sim.github.io/pytao/).
Authorship and licensing are described in [ATTRIBUTION.md](ATTRIBUTION.md).
