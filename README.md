# Awesome Accelerator Skills

An agent skill for working with **Bmad, Tao, and PyTao** from authoritative
documentation and reproducible examples.

- **Bmad** defines the accelerator physics conventions, lattice language,
  element attributes, and native library routines.
- **Tao** is the interactive program for model inspection, optics, fitting,
  optimization, and tracking.
- **PyTao** provides a Python interface to Tao.

The [`bmad-ecosystem`](skills/bmad-ecosystem/SKILL.md) skill routes each task
to the relevant layer. Its short entry point loads focused guides as needed;
the upstream manuals and API sources supply the detailed authority.

## Install

Clone this repository and install the entire `skills/bmad-ecosystem` directory
in the skill search path supported by your agent. Preserve its subdirectories,
`LICENSE`, and `ATTRIBUTION.md` when copying it.

For a project whose agent discovers `.agents/skills`:

```bash
git clone https://github.com/ndwang/awesome-accelerator-skills.git
mkdir -p /path/to/project/.agents/skills
cp -R awesome-accelerator-skills/skills/bmad-ecosystem /path/to/project/.agents/skills/
```

For Claude Code, the repository also includes a plugin manifest:

```bash
claude --plugin-dir /path/to/awesome-accelerator-skills
```

Use your client's documented skill installation or reload procedure. The skill
uses the [Agent Skills format](https://agentskills.io/specification); discovery
paths and available execution tools depend on the client.

Example requests:

- "Use the Bmad ecosystem skill to explain the coordinates in my particle file."
- "Find why this Bmad lattice fails to load, and verify the repaired optics in Tao."
- "Use PyTao to scan a quadrupole and save downstream beta functions to CSV."
- "Locate the manual section defining this Tao datum and check my installed version."

## Documentation

The skill includes focused guides for [Bmad](skills/bmad-ecosystem/references/bmad.md),
[Tao](skills/bmad-ecosystem/references/tao.md),
[PyTao](skills/bmad-ecosystem/references/pytao.md), and
[end-to-end workflows](skills/bmad-ecosystem/references/workflows.md).
The [documentation guide](skills/bmad-ecosystem/references/documentation.md)
maps tasks to upstream source files and explains version selection.

Use the documentation that matches your installed software first. The
[source manifest](skills/bmad-ecosystem/sources.lock.json) pins fallback
Bmad/Tao and PyTao sources by commit and file hash. Full manuals are obtained
on demand. Existing checkouts and the official websites work with ordinary
file-search and browsing tools.

An **optional**, Python 3.10+ standard-library helper can fetch and search a
pinned documentation cache:

```bash
python skills/bmad-ecosystem/scripts/docs.py --cache /path/to/bmad-docs fetch --project all
python skills/bmad-ecosystem/scripts/docs.py --cache /path/to/bmad-docs search 'canonical momentum' --project bmad
python skills/bmad-ecosystem/scripts/docs.py --cache /path/to/bmad-docs list --project tao
```

Fetching requires network access or the matching local source checkout.
Searching and reading the resulting cache work offline. The skill uses the
agent's available tools to inspect PDF pages when a figure or layout matters.

## Runtime example

The [FODO example](skills/bmad-ecosystem/assets/fodo/fodo.bmad) is a small open
electron beamline with specified entrance optics. PyTao examples require a
working Tao shared library as well as the Python package.

```bash
python skills/bmad-ecosystem/scripts/doctor.py
python skills/bmad-ecosystem/scripts/scan_quadrupole.py --help
```

The scan example recalculates the model for each quadrupole setting, writes
the requested optics, and restores the original setting after success or
failure. See its command-line help for lattice and output options.

## Development and validation

Run the offline tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

CI runs these tests and validates the skill with the Agent Skills reference
validator. [Acceptance tasks](tests/acceptance.md) cover source retrieval,
lattice diagnostics, and PyTao scans. Real Tao execution is an additional
validation step when that runtime is installed; format validation alone does
not establish accelerator physics correctness.

The skill is self-contained under `skills/bmad-ecosystem`, so it can be copied
or included from a pinned repository checkout by a downstream skill collection.
Genesis-specific contribution and submodule tooling changes are separate work.

## License

Original repository content is **GPL-3.0-only**, following the GPL version 3
licenses used by Bmad and PyTao. See [LICENSE](LICENSE) and the skill's
[upstream attribution](skills/bmad-ecosystem/ATTRIBUTION.md). Cached upstream
documentation retains its original copyright and license notices.
