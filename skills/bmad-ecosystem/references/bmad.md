# Bmad: physics, lattice definitions, and library use

Use documentation matching the user's Bmad installation first. The source links below pin the fallback reference revision recorded in [sources.lock.json](../sources.lock.json); a documentation revision does not select or install a runtime.

## Find the right source

| Question | Read or search |
| --- | --- |
| Phase-space definitions, reference time, conversion to other codes | [Phase Space Coordinates][phase], especially `s:phase.space` |
| Local, element, and floor coordinate frames | [Coordinates][coordinates] |
| Statements, element matching, expansion, includes | [Lattice File Format][lattice] and [Lines and Lists][lines] |
| Species, reference energy, initial Twiss parameters | [Parameter Statements][parameters] |
| Tracking method choice and supported element combinations | [Tracking Methods][methods] and [Tracking][tracking] |
| Native library types and calling conventions | [Programming][programming], then the matching [interfaces][interfaces] and [structures][structures] |

Read the surrounding section, including qualifications and definitions. For equations or diagrams whose meaning is unclear in text, consult the corresponding manual page with whatever PDF capability the host agent provides. See [documentation.md](documentation.md) for source access.

## Establish the physical model before editing

Record the reference species, tracked species if different, energy or momentum, `open` or `closed` geometry, initial optics, branch, and requested observable. Inspect included lattice files and startup scripts before replacing a value that may be set elsewhere.

- Set `parameter[geometry]` explicitly in a new example. An open lattice propagates specified initial orbit and Twiss parameters; closed geometry requests periodic optics and closed-orbit calculations. `closed` does not establish geometrical closure in floor coordinates. [Source][parameters]
- Distinguish `E_tot` (total energy) from kinetic energy. Bmad's `p0c` denotes reference momentum times the speed of light, expressed in eV. The MAD-compatible `beam, energy = ...` statement instead uses GeV. Check the syntax being used before copying a number. [Source][parameters]
- Specify appropriate `beginning[beta_a]`, `beginning[alpha_a]`, `beginning[beta_b]`, and `beginning[alpha_b]` for an open lattice. Keep mode labels `a` and `b` in coupled calculations rather than silently relabeling them as horizontal and vertical. [Sources][parameters] [Optics][optics]
- Preserve the user's selected tracking method, RF timing, radiation, and collective effects unless the task requires changing them. A successful parser run establishes syntax, not the adequacy of the physics model.

## Use the charged-particle coordinates precisely

For ordinary longitudinal-position-based charged-particle tracking, the coordinate vector is

\[
\mathbf r(s)=(x,p_x,y,p_y,z,p_z),\qquad
p_x=\frac{P_x}{P_0},\quad p_y=\frac{P_y}{P_0},\quad
p_z=\frac{P-P_0}{P_0}.
\]

Here `P` is the magnitude of the particle momentum and `P0` is the reference momentum at that location. The longitudinal coordinate is

\[
z=-\beta c\,[t-t_0],
\]

where `beta` is the **particle's** speed divided by `c`, and `t0` is the reference arrival time at the same `s`. An earlier arrival has positive `z`. `p_z` is a relative momentum deviation, and `z` is defined through arrival time. The local-frame longitudinal position and the longitudinal momentum component are different quantities. [Source: Charged Particle Phase Space Coordinates][phase]

Keep these consequences explicit when answering or converting distributions:

- `p_x` and `p_y` are normalized momenta; a slope such as `dx/ds` requires the appropriate conversion.
- The reference momentum can change through an accelerating lattice. Use the local reference values when reconstructing physical momentum.
- Replacing `p_z` by a relative energy deviation or setting `beta = 1` is an approximation whose regime must be stated.
- Consult the separate time-based and photon sections before handling those representations; the vector above is for ordinary charged-particle tracking.

## Build and diagnose a lattice

1. Use the existing project layout, or copy the small [FODO example](../assets/fodo/fodo.bmad) into a working directory.
2. Define elements with Bmad syntax, for example `qf: quadrupole, l = 0.2, k1 = 1.0`; assemble a `line`, then select it with `use, line_name`.
3. Load the lattice through Tao or the user's Bmad application. Inspect the first parser error, including its file and line. Fix one cause at a time and reload from clean initial state.
4. Inspect the expanded lattice: element type, length, count, reference momentum, branch, and the actual changed attribute. Wildcard assignments may match zero elements without a parser error.
5. Validate the requested physics observable and a relevant invariant or limiting case. For example, verify finite positive beta functions for an optics example and check the direction of a small perturbation.

Bmad statements are generally case insensitive, with exceptions including filenames and some string data. Repeated line entries can produce several elements with the same name. Use explicit branch and occurrence selectors when needed: `2>>45` selects element 45 of branch 2, and `QF##2` selects the second matching occurrence in a branch. Check which expanded objects are controlled by a lord before changing slaves independently. [Source][lattice]

Bmad normally adds an `END` marker automatically. Avoid introducing a second element with that name in a minimal example; inspect `parameter[no_end_marker]` if explicit control is needed. [Source][parameters]

For superposition, multipass, field maps, wakes, space charge, spin, or X-ray optics, read the corresponding manual chapter and a matching upstream example. State which effects the model actually enables; do not infer them from an element's name.

## Work on the native library

Use the installed release's module interfaces and examples. Inspect `lat_struct`, `branch_struct`, `ele_struct`, and `coord_struct` where relevant; preserve Bmad's parsing and bookkeeping procedures when attributes change. Start from the documented example program and the closest working call site before adding a routine call. Compile and run the smallest representative case against the user's actual build. Report the compiler/build, source revision when known, and whether the test exercised the native library or only a higher-level wrapper. [Programming source][programming]

[phase]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/bmad/doc/phase-space.tex
[coordinates]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/bmad/doc/coordinates.tex
[lattice]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/bmad/doc/lattice-file.tex
[lines]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/bmad/doc/lines-and-lists.tex
[parameters]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/bmad/doc/param-statements.tex
[methods]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/bmad/doc/methods.tex
[tracking]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/bmad/doc/tracking.tex
[optics]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/bmad/doc/optics.tex
[programming]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/bmad/doc/programming.tex
[interfaces]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/bmad/modules/bmad_interface.f90
[structures]: https://github.com/bmad-sim/bmad-ecosystem/blob/6ac367f165955c971a3cad5a1858c09b246471b6/bmad/modules/bmad_struct.f90
