# Bmad: the physical model and lattice language

Bmad is a library for accelerator and X-ray simulations. A Bmad lattice describes
the machine: its elements, their arrangement, fields, reference particle, and
modeling choices. It does not contain commands to plot optics or run an optimizer;
those actions belong to a program such as [Tao](tao.md). [PyTao](pytao.md) lets
Python, including an agent's Python session, operate that program.

## How a lattice is organized

- An **element** represents a magnet, cavity, drift, aperture, optical component,
  or a named location such as a marker. Its attributes specify length, strength,
  alignment, and other properties.
- A **line** is a lattice-file expression assembling elements and other lines.
  Bmad expands the selected lines into **branches**: ordered paths through the
  machine.
- A **lattice** contains one or more branches. A branch can describe a beamline,
  a storage ring, or one repeating period. Fork elements connect branches.
- A **lord** controls other elements, its **slaves**. This represents shared
  knobs, overlapping fields, or several passes through the same physical magnet.
  The physical elements and the elements used for tracking need not be identical.

Each branch starts with `BEGINNING` at element index 0. Bmad also appends an
`END` marker by default. Repeating a line can create multiple elements with the
same name; element names alone are therefore not always unique.

These objects are defined in the manual's **Bmad Concepts and Organization**
chapter ([source](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad/doc/concepts.tex),
labels `s:element.def`, `s:branch.def`, `s:lattice.def`, and `s:lord.slave`).

## Read a small lattice

The bundled [lattice](../assets/beamline/lattice.bmad) comes from the official
[`simple.bmad` tutorial](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad-doc/tutorial_bmad_tao/lattice_files/simple.bmad).
Its essential statements are:

```bmad
beginning[beta_a] = 10.
beginning[beta_b] = 10.
beginning[e_tot] = 10e6
parameter[geometry] = open
parameter[particle] = electron

d: drift, l = 0.5
b: sbend, l = 0.5, g = 1, e1 = 0.1, dg = 0.001
q: quadrupole, l = 0.6, k1 = 0.23

lat: line = (d, b, q)
use, lat
```

`beginning` supplies entrance conditions; here the two mode beta functions are
10 m and the reference total energy is 10 MeV. `parameter` supplies the species
and geometry. The next three statements define elements, `line` orders them,
and `use` selects the line that becomes the lattice.

For the bend, `g` sets the design curvature and `dg` adds a field error without
changing that design curvature. For the quadrupole, `k1` is a normalized strength
in m^-2. The [element guide](bmad/elements.md) explains these distinctions.

## Geometry and initial conditions

An **open** branch propagates the specified entrance orbit and optics downstream.
A **closed** branch asks the application for a closed orbit and periodic optics.
Choosing `closed` does not move magnets to close the machine in floor coordinates;
it is also useful for studying a single periodic cell.

For a new open lattice, specify `beginning[beta_a]`, `beginning[alpha_a]`,
`beginning[beta_b]`, and `beginning[alpha_b]` as appropriate. The `a` and `b`
labels denote normal modes; they need not coincide with the horizontal and
vertical planes when the motion is coupled.

`e_tot` means total energy, including rest energy. `p0c` is reference momentum
times the speed of light; both are expressed in eV. Set either one to establish
the reference energy/momentum. Individual particles can differ from that
reference, and accelerating elements can change the reference along the lattice.

See [physics conventions](bmad/physics-conventions.md) for coordinates, units,
fields, and optics. The official **Lattice File Global Parameters** chapter
([source](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad/doc/param-statements.tex),
`s:param` and `s:beginning`) gives the complete setup options.

## Choose a topic

| Task | Read |
| --- | --- |
| Write or understand definitions, expressions, lines, includes, and element selectors | [Lattice syntax](bmad/lattice-syntax.md) |
| Choose an element or understand its main attributes | [Elements](bmad/elements.md) |
| Interpret particle coordinates, energy, RF phase, fields, or Twiss quantities | [Physics conventions](bmad/physics-conventions.md) |
| Represent shared knobs, alignment supports, and lord/slave relationships | [Controllers](bmad/controllers.md) |
| Insert overlapping elements or model repeated passes | [Lattice composition](bmad/lattice-syntax.md#superposition-and-multipass) |
| Load the lattice and inspect calculated quantities | [Tao](tao.md) or [PyTao](pytao.md) |

## Capabilities beyond the basic lattice

| Capability | Meaning and official starting point |
| --- | --- |
| Field maps | Represent spatially varying fields rather than only idealized element strengths. **Field Maps**, `s:fieldmap` in [attributes.tex](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad/doc/attributes.tex). |
| Tracking algorithms | Choose the particle integrator, transfer-matrix calculation, and spin method separately. **Tracking, Spin, and Transfer Matrix Calculation Methods**, `c:methods` in [methods.tex](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad/doc/methods.tex). |
| Collective effects | Model interactions within a bunch, including space charge and coherent synchrotron radiation. Start with [multiparticle.tex](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad/doc/multiparticle.tex) and the tutorial's [beam tracking example](https://github.com/bmad-sim/bmad-ecosystem/tree/main/bmad-doc/tutorial_bmad_tao/lattice_files/beam_tracking). |
| Wakes | Describe fields left by a bunch that act on following particles or bunches. **Wakefields**, `s:wakes` in [attributes.tex](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad/doc/attributes.tex); theory in [wakefields.tex](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad/doc/wakefields.tex). |
| Radiation and spin | Compute radiation effects and spin evolution using their own settings and algorithms. See [synchrotron-radiation.tex](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad/doc/synchrotron-radiation.tex) and [spin.tex](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad/doc/spin.tex). |
| Photon optics | Model emission and transport through crystals, mirrors, apertures, and other X-ray elements. See [elements](bmad/elements.md#photon-optics) and [xray-tracking.tex](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad/doc/xray-tracking.tex). |
| Native applications | Call Bmad from a program through its lattice, element, and particle structures. Start with [programming.tex](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad/doc/programming.tex) and the official [example program](https://github.com/bmad-sim/bmad-ecosystem/blob/main/bmad/doc/example-program.tex). |

The [Bmad manual](https://www.classe.cornell.edu/bmad/manual.html) is the full
reference. The [Bmad/Tao tutorial examples](https://github.com/bmad-sim/bmad-ecosystem/tree/main/bmad-doc/tutorial_bmad_tao/lattice_files)
are useful starting points for particular features. Source links above name the
chapter and, where useful, its TeX label so a large file can be searched directly.
