# Acceptance tasks

Run these tasks with a fresh agent that has the installed skill and ordinary
file, shell, and documentation access. Provide the task and relevant user
files; avoid supplying a prepared solution or an earlier agent's diagnosis.

## Bmad coordinate interpretation

Prompt: "Use the Bmad ecosystem skill to explain what x, px, y, py, z, and pz
mean in a Bmad particle file. Explain what additional reference information
is needed to interpret them, and cite the authoritative definitions."

Check that the answer locates upstream definitions, distinguishes normalized
canonical momenta and relative longitudinal coordinates, identifies units and
reference quantities, and reports the source version. Judge against the
actual manual section, not a memorized keyword list.

## Repair a lattice

Supply a copy of the bundled FODO lattice with one realistic parsing or
initialization error. Prompt: "Load this lattice with Tao, fix the reported
error, and show a reproducible check of the resulting optics."

Check that the agent captures the original diagnostic, makes a targeted
correction, reruns the load and optics calculation, and describes the open
line's entrance conditions. Preserve the original fixture for comparison.

## Python scan

Prompt: "Use PyTao to scan the focusing quadrupole in the bundled example
over three strengths, save downstream beta functions to CSV, and restore
the original lattice state."

Check the actual CSV, values and units, selected element and observation
point, runtime information, and restored original strength. Exercise an
exception during the scan to confirm restoration on failure. If the runtime
is unavailable, the agent must report that limitation instead of inventing
simulation results.

## Offline documentation

Fetch the pinned source corpus once, then disable network access. Ask for a
specific Bmad element attribute, a Tao command, and a PyTao method. Check
that searches find relevant source sections, the agent reads sufficient
context, citations identify source revisions, and notebooks retain readable
Markdown and code without presenting cached outputs as a fresh execution.
