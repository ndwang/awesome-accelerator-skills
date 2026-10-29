# Skill acceptance tasks

Use fresh agent sessions with the installed skill and the indicated input files.
Compare answers and navigation with the same tasks using the earlier skill or
without a skill. Record substantive errors, unnecessary reference loading, and
whether the agent can complete common work from the local explanation and example.
These are behavioral checks, not a list of phrases an answer must contain.

## Explain and edit a lattice

Give the agent `assets/beamline/lattice.bmad` and ask it to explain the reference
energy, entrance optics, and element sequence, then insert a second quadrupole
after the first. The explanation should connect each statement to the physical
model. Compare the resulting lattice with the request; load it when Tao is available.

## Interpret Bmad coordinates

Ask what `x, px, y, py, z, pz` mean in a charged-particle distribution and what
information is needed to convert them to physical momenta and arrival times.
Check against the Bmad manual's charged-particle phase-space definitions, including
momentum normalization and the particle beta in the longitudinal coordinate.

## Choose a capability and locate its details

Ask how to represent the same cavity traversed twice, and how this differs from
placing two independent copies of an element in a line. The agent should explain
the relevant concept, locate the official multipass example, and find the
specific manual section without reading all Bmad references or the entire manual.

## Prepare a Tao session and fit

Give the agent `assets/matching` and ask it to explain the distinction between
data and variables, change the target beta values, and provide the commands to
run the fit and inspect its result. Check its interpretation of the data records,
element selection, and variable bounds. With Tao available, run the changed setup
from a separate working copy and examine the requested target values and residuals.

## Use PyTao for ordinary model access

Ask the agent to load the introductory lattice from Python, read the downstream
Twiss parameters, change its quadrupole, and read the new result. Its code should
show normal `Tao()` construction and the relevant PyTao calls. Check that it uses
structured results for numerical quantities and handles paths to the input file.
Compare the API usage with the official PyTao examples linked by the guide.

## Find a Python feature

Ask how to obtain particle data or make a Matplotlib optics plot from an existing
Tao model. Check that the agent identifies the appropriate package functionality
and the corresponding official notebook. It should not need a new utility script
or a complete re-explanation of Bmad to answer the question.

For any execution task, distinguish code inspection from an actual run. An absent
runtime should be recorded as an unexecuted check, not replaced with invented results.
