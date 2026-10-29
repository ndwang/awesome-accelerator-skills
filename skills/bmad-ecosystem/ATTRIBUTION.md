# License and sources

Copyright (C) 2026 Ningdong Wang. Original skill text is licensed under
GNU General Public License version 3 only (`GPL-3.0-only`); see [LICENSE](LICENSE).

This skill explains Bmad, Tao, and PyTao using their official documentation.
The guides link to maintained documentation and examples. The revisions below
record the sources used to prepare this edition, rather than selecting the
software version that a user must run.

| Source | Revision consulted |
| --- | --- |
| [Bmad ecosystem](https://github.com/bmad-sim/bmad-ecosystem) | `f20a022651c4c2834c3ba32cf45d643b7cee9df1` |
| [PyTao](https://github.com/bmad-sim/pytao) | `c22d07778faf2b70f28a914362e215e5bb9ced25` |

## Bundled examples

The following files are copied from David Sagan and contributors' Bmad/Tao
tutorial at the Bmad ecosystem revision above. Their contents are unchanged;
`simple.bmad` is installed under the name `lattice.bmad`.

| Bundled path | Upstream source |
| --- | --- |
| `assets/beamline/lattice.bmad` | [tutorial_bmad_tao/lattice_files/simple.bmad](https://github.com/bmad-sim/bmad-ecosystem/blob/f20a022651c4c2834c3ba32cf45d643b7cee9df1/bmad-doc/tutorial_bmad_tao/lattice_files/simple.bmad) |
| `assets/matching/lat.bmad` | [lattice_optimization/lat.bmad](https://github.com/bmad-sim/bmad-ecosystem/blob/f20a022651c4c2834c3ba32cf45d643b7cee9df1/bmad-doc/tutorial_bmad_tao/lattice_files/lattice_optimization/lat.bmad) |
| `assets/matching/tao.init` | [lattice_optimization/tao.init](https://github.com/bmad-sim/bmad-ecosystem/blob/f20a022651c4c2834c3ba32cf45d643b7cee9df1/bmad-doc/tutorial_bmad_tao/lattice_files/lattice_optimization/tao.init) |
| `assets/matching/setup.tao` | [lattice_optimization/setup.tao](https://github.com/bmad-sim/bmad-ecosystem/blob/f20a022651c4c2834c3ba32cf45d643b7cee9df1/bmad-doc/tutorial_bmad_tao/lattice_files/lattice_optimization/setup.tao) |

Bmad's [copyright notice](assets/BMAD-COPYRIGHT) identifies GNU GPL version 3.
The bundled license text is from the consulted
[PyTao LICENSE](https://github.com/bmad-sim/pytao/blob/c22d07778faf2b70f28a914362e215e5bb9ced25/LICENSE).
Upstream files retain their authorship and any file-specific notices.

## Python examples

Python patterns in the guide are drawn from the official PyTao usage guide,
API documentation, and example notebooks linked beside each topic. The full
notebooks remain upstream, including their own input files and dependencies.

This is an independent community skill, not an official Bmad project release.
