# Workflows and verification

Use the smallest workflow that answers the user's question. Establish the requested observable, units, coordinate convention, installation, and input files before expanding the task. Treat the checks below as task-specific evidence to collect, rather than a reason to run unrelated simulations.

## Answer a manual question

1. Identify whether the question concerns Bmad physics/lattice syntax, Tao commands, or the PyTao interface.
2. Search the corresponding manual or source matching the user's version. Use [documentation.md](documentation.md) to locate sources; the bundled retrieval script is optional.
3. Read the full relevant section around the search match. Follow definitions when a symbol, normalization, unit, or exception controls the answer.
4. Give the answer and cite the manual section or source file/revision. Separate a documented statement from your own derivation or approximation.

For example, a question about Bmad `pz` belongs in the Bmad manual's phase-space chapter; a question about the dictionary returned by `ele_twiss` belongs in the installed PyTao implementation. A PDF search hit or a generated API page containing only an autodoc directive may require the underlying source before it answers the question.

## Create or repair a lattice

1. Inspect existing files, including includes and initialization. Preserve the user's species, energy, geometry, naming, and initial optics unless a change is part of the task.
2. Consult [bmad.md](bmad.md) for syntax and conventions. For a new minimal example, copy [fodo.bmad](../assets/fodo/fodo.bmad) and [tao.init](../assets/fodo/tao.init) into a working directory.
3. Load the files in Tao with plotting disabled when appropriate. Capture the actual startup and first parser error; diagnose its source before changing subsequent lines.
4. Inspect the expanded lattice and the changed attributes. Verify that the correct branch, element occurrences, and reference momentum were selected.
5. Calculate the requested observable and check a physical expectation relevant to that task. Reload the saved inputs in a fresh session when verifying a repair or export.

A useful result contains the edited inputs, reproduction command, runtime version when available, and the observed check. If Tao is unavailable, state that the work has had a source/syntax review and still needs an execution check. Do not present an unexecuted lattice as validated.

## Inspect optics in Tao

Use [tao.md](tao.md) and the example [inspect.tao](../assets/fodo/inspect.tao). Establish the universe, branch, and model/design/base state, then inspect element identity and the needed optics. Check finite results, positive beta functions where applicable, and whether the lattice was actually recalculated after changes. Use an independent analytic limit when it is simple and meaningful, such as drift propagation for an uncoupled case.

For a closed ring, examine stability and periodic/closed-orbit success before interpreting tunes or Twiss parameters. For an open beamline, verify the initial optics used for propagation. A headless plotting error and a failed optics calculation require different remedies; preserve diagnostics so the distinction can be made.

## Automate a parameter scan with PyTao

Use [pytao.md](pytao.md) and [scan_quadrupole.py](../scripts/scan_quadrupole.py). Read the script's `--help` before supplying custom inputs.

1. Evaluate the initial point and save original parameter values plus calculation/plot flags.
2. Resolve the knob and observation element unambiguously; record the universe, branch, state, units, and sample grid.
3. Apply each sample, force the required calculation if it was deferred, and validate the observable's shape and finiteness. Check physical validity in addition to numerical validity.
4. Restore the initial state even if a command or measurement fails. Verify the restored parameter and baseline observable.
5. Save a table with the scanned value, observable, units, and a failure status for rejected points where the workflow continues after failure. Report any missing samples.

The bundled script is a small optics demonstration. Adapt a scan to the user's lattice and physics model; convergence of this example is not a validation of collective effects, RF timing, or a different tracking algorithm.

## Fit optics or an orbit

Start from the [Tao fitting procedure](tao.md#configure-fitting-deliberately). Define knobs and limits, targets and weights, and active data explicitly. Check a small response before invoking the optimizer. Record the starting model, stopping criteria, final residuals, any bound saturation, and invalid evaluations. Reload the exported result and recompute the targets before calling the fit reproducible.

For stochastic tracking, record the random seeds and particle count, and compare meaningful ensemble statistics. Use a convergence check in the numerical parameter that can affect the claimed result, such as a tracking step or space-charge mesh; avoid applying a fixed universal tolerance across unrelated observables.

## Diagnose environment failures

Use [doctor.py](../scripts/doctor.py) as an optional inventory, then make the diagnosis specific:

| Symptom | Next evidence to collect |
| --- | --- |
| `pytao` cannot import | Python executable, installed package/version, import traceback |
| Tao shared library cannot load | Exact library-loading error, intended build, dependency discovery from that environment |
| Files are missing at startup | Working directory, init filename, includes, environment-variable expansion |
| Command or returned key differs | Installed Tao help, PyTao method signature/source, actual raw response |
| Optics fail after a change | Changed attributes, active calculation flags, initial/periodic boundary conditions, full calculation diagnostic |
| Results differ between tools | Coordinate definitions, reference momentum, units, initial distribution, enabled physics, numerical settings |

Make one supported change and rerun the smallest failing operation. Preserve useful failure output. Avoid reinstalling a working environment or changing the physics merely to suppress an error.

## Report a completed task

State what changed, why it answers the request, which inputs and runtime produced the result, and which calculation was actually run. Include concrete values with units when relevant. Cite the authoritative sources used for conventions or version-sensitive behavior. Distinguish verified behavior from remaining limits; retain the commands and files needed to reproduce the result.
