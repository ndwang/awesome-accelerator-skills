# Find authoritative documentation

Use the manual or source matching the installed software when an answer depends
on version. Read a targeted section, preserve its units and qualifications, and
cite the chapter or source path. The bundled guides are navigation and workflow
advice; the upstream sources define the physics, syntax, and API behavior.

## Choose the source

| Question | Start here | Useful source files |
| --- | --- | --- |
| Bmad coordinates, normalization, signs, units | [Bmad manual](https://www.classe.cornell.edu/bmad/manual.html) | `bmad/doc/coordinates.tex`, `phase-space.tex`, `electromagnetic-fields.tex` |
| Lattice syntax and element attributes | Bmad manual | `bmad/doc/lattice-file.tex`, `elements.tex`, `attributes.tex`, `methods.tex` |
| Tracking, wakes, collective effects | Bmad manual | `bmad/doc/tracking.tex`, `charged-tracking.tex`, `multiparticle.tex`, `wakefields.tex` |
| Bmad library programming | Bmad programmer's guide | `bmad/doc/programming.tex`, `lat-struct.tex`, `ele-struct.tex`, `subroutines.tex` |
| Tao startup, commands, data, fitting | [Tao manual](https://www.classe.cornell.edu/bmad/tao.html) | `tao/doc/initialization.tex`, `syntax.tex`, `command-list.tex`, `data.tex`, `variables.tex`, `optimization.tex` |
| Tao's machine interface | Tao manual and installed help | `tao/doc/pipe-interface.tex`, `pipe-interface-commands.tex` |
| PyTao initialization and methods | [PyTao documentation](https://bmad-sim.github.io/pytao/) and installed signatures | `docs/usage.md`, `docs/installation.md`, `pytao/tao.py`, `core.py`, `interface_commands.py`, `subproc.py` |

Read the relevant guide's source links for pinned URLs. The two manual entry
files are `bmad/doc/bmad.tex` and `tao/doc/tao.tex`; their includes locate chapters.
Search exact attribute names and TeX labels, then read the surrounding section.
Preserve mathematical TeX when extracting equations.

## Use ordinary tools first

Read an existing upstream checkout with the agent's normal file tools. For
example, from a Bmad ecosystem source checkout:

```bash
rg -n 'canonical|reference momentum' bmad/doc/phase-space.tex
rg -n 'lattice_calc_on' tao/doc/command-list.tex
sed -n '1,100p' bmad/doc/phase-space.tex
```

For PyTao, inspect the installed method signature and docstring, or its matching
source revision, before copying an example from another release. If the only
available manual is a PDF, use the host agent's normal PDF or browser facilities.
Inspect the rendered page when a figure, table, or ambiguous equation matters.
This skill requires no PDF reader, embedding service, or special MCP server.

## Optional pinned offline cache

Use `scripts/docs.py` when a searchable local snapshot would help. It needs
Python 3.10+ and the standard library. Set `SKILL` to the installed skill folder
and `CACHE` to a separate writable directory; run one fetch per cache at a time.

```bash
SKILL=/path/to/bmad-ecosystem
CACHE=/path/to/bmad-docs-cache
python "$SKILL/scripts/docs.py" sources
python "$SKILL/scripts/docs.py" --cache "$CACHE" fetch --project all
python "$SKILL/scripts/docs.py" --cache "$CACHE" search 'lattice_calc_on' --project tao --limit 8
python "$SKILL/scripts/docs.py" --cache "$CACHE" read tao tao/doc/command-list.tex --start 1190 --lines 55
python "$SKILL/scripts/docs.py" list --project bmad
```

`fetch` needs network access on its first run. Subsequent search and read commands
are offline. Select `bmad`, `tao`, or `pytao` to fetch only one project. Add
`--checkout /path/to/upstream/repository` to fetch from a local source tree;
every selected file must still match its pinned blob. A locally modified or
different-version checkout can be read directly with ordinary tools instead.

The [source manifest](../sources.lock.json) pins Bmad/Tao at
`6ac367f165955c971a3cad5a1858c09b246471b6` and PyTao at
`c22d07778faf2b70f28a914362e215e5bb9ced25`. Its 164 entries cover 52 Bmad LaTeX
files, 20 Tao LaTeX files, PyTao documentation/notebooks/API source, and upstream
license notices. These are reproducible snapshots, not a claim that every
installed release has the same interface. Figures and compiled manuals are not
part of the text cache.

Each downloaded file is checked against its upstream Git blob hash before the
catalog is activated. Reads check the hash again. Raw bytes and license notices
are retained. Notebook search uses markdown and code-cell inputs; saved outputs
are omitted and never count as evidence that an example ran successfully.
Notebook line numbers refer to the displayed input view. Use `read --raw` when
the original notebook JSON is needed.

Search is a case-insensitive literal substring search; use `--regex` explicitly
for regular expressions. Use several short, specific queries when TeX markup or
line wrapping prevents a phrase match. Read beyond the hit before drawing a
conclusion. Searches cover only the selected projects and fail if their pinned
cache is unavailable. A missing hit does not establish that a feature is absent.

To update a snapshot, deliberately choose upstream commits, regenerate the file
list and Git blob hashes from those commits, review the changed documentation,
and fetch into a cache before relying on it. Keep attribution and version notes
with any redistributed source material.
