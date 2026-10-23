---
name: bmad-ecosystem
description: Use Bmad, Tao, and PyTao for accelerator modeling. Apply this skill when writing or debugging Bmad lattices, checking physics or coordinate conventions, operating Tao, configuring optics or optimization, scripting Tao through Python, or locating authoritative documentation for these tools. Route questions to the Bmad library and lattice manual, the Tao user manual, or the PyTao API as appropriate; verify syntax and behavior against the user's installed version.
license: GPL-3.0-only
metadata:
  author: Ningdong Wang
  version: "2.0.0"
---

# Bmad, Tao, and PyTao

## Choose the right layer

| Task | Authority | Read next |
| --- | --- | --- |
| Physics, coordinates, units, element attributes, lattice syntax, or native library routines | Bmad | [Bmad guide](references/bmad.md) |
| Interactive commands, initialization, universes, data, variables, optimization, or plots | Tao | [Tao guide](references/tao.md) |
| Python initialization, returned data, automation, subprocesses, or library loading | PyTao | [PyTao guide](references/pytao.md) |
| Locate a manual section, API definition, or versioned source | Upstream documentation | [Documentation access](references/documentation.md) |
| Build, diagnose, scan, or optimize a model across layers | Task workflow | [Workflows](references/workflows.md) |

Treat Bmad as the physics and lattice library, Tao as the user program built
on Bmad, and PyTao as a Python interface to Tao. Follow the authority for the
layer being changed; a Python method can expose a Tao operation without
changing Bmad's physical meaning.

## Establish the model and runtime

1. Inspect the user's lattice, includes, `tao.init`, command files, scripts,
   and existing conventions. Identify species, reference momentum or energy,
   lattice geometry, universes, branches, and the observable requested.
2. Determine available executables, Python environment, PyTao version, and
   Tao shared-library location. Use ordinary environment checks or the
   optional [diagnostic script](scripts/doctor.py). Keep dependency installation
   consistent with the user's environment.
3. Prefer documentation supplied with that installation or checked out at
   the matching revision. Use the pinned source set in
   [sources.lock.json](sources.lock.json) as a reproducible fallback, and
   state any mismatch with the installed runtime.
4. Resolve consequential ambiguity before interpreting results: open line
   versus closed ring, particle versus reference quantities, coordinate
   normalization, observation location, and what is held fixed in a scan.
   Use existing project conventions for routine choices.

## Retrieve the needed documentation

Read the relevant guide above, then search authoritative sources using
specific terms: element or attribute names, a Tao command, a datum type,
or a PyTao method. Read the surrounding section, including prerequisites,
units, caveats, and definitions. Follow an upstream cross-reference when the
section depends on another definition.

Use normal file search and reading against an existing documentation checkout,
or browse the linked upstream documentation. The optional
[documentation helper](scripts/docs.py) can fetch a pinned corpus and perform
offline searches after it has been cached. A task does not require this helper.
See [documentation access](references/documentation.md) for source locations,
manual links, and helper commands.

For equations, inspect the LaTeX source and its variable definitions. If a
diagram or layout affects the interpretation, view the corresponding manual
page with the host's available document tools. Distinguish a PDF page index
from the manual's printed page number. Cite the manual section or source
path and revision; preserve enough context for the user to verify the claim.

## Implement and verify

- Confirm element attributes and tracking methods against Bmad's element
  documentation. Check units, signs, and reference quantities before translating
  a formula or another code's lattice into Bmad.
- Check Tao's installed `help` output for version-sensitive commands. Inspect
  the selected universe, branch, and model/design/base state before reading
  or changing an element.
- Inspect the installed PyTao signature and return type before using an API.
  Prefer a documented typed method when it expresses the operation; retain
  raw Tao commands when they are the appropriate interface.
- Run a minimal parse/load check first. Resolve diagnostics at their source,
  then verify the requested observable and a relevant physics consistency
  check. Choose checks appropriate to an open line or a closed ring.
- Save the original values and calculation state before a scan. Restore them
  in `finally`, including after a failed calculation. Collect results only
  after the lattice has been recalculated. Keep units in saved data.
- Preserve the user's source lattice unless editing it is the task. Use a
  working copy for exploratory runs and record which inputs produced the result.

Use the bundled [FODO lattice](assets/fodo/fodo.bmad),
[Tao initialization](assets/fodo/tao.init), and
[inspection commands](assets/fodo/inspect.tao) for a small starting example.
It is an open beamline with specified entrance optics. Run the optional
[quadrupole scan](scripts/scan_quadrupole.py) for a reproducible Python example;
check `--help` for its inputs and output. It requires PyTao and a working Tao
library; the guides and documentation helper remain usable without them.

## Report the result

Report the changed files or commands, the runtime and documentation versions,
the checks actually run, the observable with its units, and any remaining
assumptions or limitations. Distinguish syntax validation, a successful model
calculation, and a physics conclusion. Include a reproducible command or a
small example when it helps the user continue the work.

## License and sources

Use the skill under [GPL-3.0-only](LICENSE). Preserve the upstream notices
described in [ATTRIBUTION.md](ATTRIBUTION.md) when copying or caching source
material.
