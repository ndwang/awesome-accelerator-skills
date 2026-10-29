# Awesome Accelerator Skills

An agent skill for [Bmad](https://www.classe.cornell.edu/bmad),
[Tao](https://www.classe.cornell.edu/bmad/tao.html), and
[PyTao](https://bmad-sim.github.io/pytao/).

The skill supplies the domain knowledge needed to write and understand Bmad
lattices, prepare Tao initialization files and commands, and work with PyTao.
It explains concepts and common usage, then points to official documentation
for complete syntax and detailed physics. PyTao also gives an agent a Python
interface for running and inspecting a model.

## Contents

[`skills/bmad-ecosystem/SKILL.md`](skills/bmad-ecosystem/SKILL.md) introduces
the three layers and links directly to task-specific references.

| Guide | Topics |
| --- | --- |
| [Bmad](skills/bmad-ecosystem/references/bmad.md) | Lattice organization and capabilities; focused references for syntax, elements, physics conventions, and controllers |
| [Tao](skills/bmad-ecosystem/references/tao.md) | Session concepts; focused references for initialization, commands/scripts, and data/fitting |
| [PyTao](skills/bmad-ecosystem/references/pytao.md) | Ordinary `Tao()` use, structured results, models, plotting, tracking, and official Python examples |

The package includes the official Bmad/Tao tutorial's
[introductory lattice](skills/bmad-ecosystem/assets/beamline/lattice.bmad)
and [optics fitting example](skills/bmad-ecosystem/assets/matching/tao.init).
Other curated examples are linked beside their relevant topics, including
PyTao's own notebooks. See
[ATTRIBUTION.md](skills/bmad-ecosystem/ATTRIBUTION.md) for copied files and sources.

## Install

Install the whole `skills/bmad-ecosystem` directory in the skill search path
supported by your agent. Keep its references, assets, license, and attribution
together. It uses the [Agent Skills format](https://agentskills.io/specification).

For a project that discovers skills in `.agents/skills`:

```sh
git clone https://github.com/ndwang/awesome-accelerator-skills.git
mkdir -p /path/to/project/.agents/skills
cp -R awesome-accelerator-skills/skills/bmad-ecosystem /path/to/project/.agents/skills/
```

The repository also supplies a Claude Code plugin manifest:

```sh
claude --plugin-dir /path/to/awesome-accelerator-skills
```

When upgrading from the earlier three-skill edition, remove the installed
`bmad`, `tao`, and `pytao` skill directories after installing `bmad-ecosystem`.
This avoids activating overlapping editions. The repository itself now contains
the combined skill only.

Reading the skill does not require Bmad. Running examples requires a working
Tao installation; Python execution also requires PyTao and its Tao shared library.
See [PyTao installation](https://bmad-sim.github.io/pytao/installation/).

## Example requests

- "Explain this Bmad lattice and change the quadrupole strengths."
- "What do the six coordinates in this Bmad particle distribution mean?"
- "Prepare a tao.init file with two universes."
- "Find the Tao commands to match the downstream beta functions."
- "Use PyTao to load this model and plot its optics."

## Development

CI checks the skill format with the Agent Skills reference validator:

```sh
python -m pip install skills-ref==0.1.1
agentskills validate skills/bmad-ecosystem
```

[Acceptance tasks](tests/acceptance.md) exercise the skill's domain explanations,
reference navigation, and ordinary Tao/PyTao usage. Run execution tasks in an
environment with the corresponding runtime. Package validation alone does not
exercise a lattice calculation.

## License

Original repository content is licensed under [GPL-3.0-only](LICENSE), as is
the standalone skill. Bundled upstream examples retain their notices and
[attribution](skills/bmad-ecosystem/ATTRIBUTION.md).
