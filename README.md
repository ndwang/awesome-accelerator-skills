# Awesome Accelerator Skills

Agent skills for the [Bmad](https://www.classe.cornell.edu/bmad) accelerator simulation
toolkit, the [Tao](https://www.classe.cornell.edu/bmad/tao.html) program, and [PyTao](https://bmad-sim.github.io/pytao/) (the Python interface to Tao). Compatible with
Claude Code, OpenAI Codex, VS Code / GitHub Copilot, OpenClaw, Google Antigravity, and any
tool that supports the open Agent Skills standard.

## What's Included

### Bmad Skill
Write, read, and understand Bmad lattice files for charged particle and X-ray simulation.

- **SKILL.md** (450 lines) -- Core lattice syntax, element types, examples, physics essentials
- **references/elements.md** -- All ~50 element types with attributes and usage
- **references/attributes.md** -- Apertures, field maps, misalignments, wakes, fringe control
- **references/lattice-syntax.md** -- Superposition, multipass, beam init, custom attributes
- **references/physics-conventions.md** -- Coordinates, phase space, fields, optics, SR
- **references/tracking-methods.md** -- All tracking/matrix methods, PTC, spin, X-ray

### Tao Skill
Operate Tao for accelerator optics simulation, optimization, and analysis.

- **SKILL.md** (396 lines) -- Commands, concepts, workflows
- **references/commands-reference.md** -- Full command reference with syntax and examples
- **references/concepts-and-syntax.md** -- Universes, branches, element addressing, expressions
- **references/initialization.md** -- Startup files, command-line options, lattice loading
- **references/data.md** -- Datum types, d1/d2 arrays, data sources
- **references/variables.md** -- Variable definitions, v1 arrays, attribute linking
- **references/optimization-and-wave.md** -- Optimizers, merit function, wave analysis
- **references/plotting.md** -- Plot setup, templates, graph and curve customization
- **references/pipe-interface.md** -- External-process communication via the pipe protocol
- **references/single-mode.md** -- Non-interactive single-command operation

### PyTao Skill
Script Tao from Python using pytao, the Python interface to Tao/Bmad.

- **SKILL.md** (262 lines) -- Initialization, API layers, data models, common patterns
- **references/api-reference.md** -- Method signatures, parameters, and return types

## Installation

These skills follow the open [Agent Skills](https://agentskills.io/home) standard
and work with any compatible harness. Pick the section that matches your tool.

<details>
<summary><strong>Claude Code</strong></summary>

**As a plugin** (recommended — keeps skills out of your project tree):
```bash
claude --plugin-dir /path/to/bmad_skills
```

**Project-level** (committed to version control, shared with collaborators):
```bash
cp -r skills/* /path/to/project/.claude/skills/
```

**Personal** (available in every project on your machine):
```bash
cp -r skills/* ~/.claude/skills/
```

</details>

<details>
<summary><strong>OpenAI Codex</strong></summary>

Codex scans `.agents/skills/` in your repo (project) and `~/.codex/skills/` (personal).

**Project-level:**
```bash
cp -r skills/* /path/to/project/.agents/skills/
```

**Personal:**
```bash
cp -r skills/* ~/.codex/skills/
```

Codex detects new skills automatically. If one doesn't appear, restart Codex.

</details>

<details>
<summary><strong>VS Code / GitHub Copilot</strong></summary>

Copilot discovers skills in `.github/skills/` (project) and `~/.copilot/skills/` (personal).

**Project-level:**
```bash
cp -r skills/* /path/to/project/.github/skills/
```

**Personal:**
```bash
cp -r skills/* ~/.copilot/skills/
```

Skills also work with the Copilot CLI and Copilot coding agent.

</details>

<details>
<summary><strong>OpenClaw</strong></summary>

OpenClaw loads skills from `<workspace>/skills/` (per-agent), `~/.openclaw/skills/` (shared
across agents), or extra directories configured via `skills.load.extraDirs` in
`~/.openclaw/openclaw.json`.

**Workspace (per-agent):**
```bash
cp -r skills/* /path/to/workspace/skills/
```

**Shared (all agents on this machine):**
```bash
cp -r skills/* ~/.openclaw/skills/
```

OpenClaw watches skill folders and picks up changes on the next agent turn.

</details>

<details>
<summary><strong>Google Antigravity</strong></summary>

Antigravity uses `.agent/skills/` (workspace) and `~/.gemini/antigravity/skills/` (global).

**Workspace:**
```bash
cp -r skills/* /path/to/workspace/.agent/skills/
```

**Global:**
```bash
cp -r skills/* ~/.gemini/antigravity/skills/
```

</details>

<details>
<summary><strong>Other Agent-Skills-compatible tools</strong></summary>

Any tool that implements the Agent Skills standard (Cursor, Gemini CLI, etc.) can use these
skills. Copy the contents of the `skills/` directory into whatever path your tool scans for
`SKILL.md` files. Consult your tool's documentation for the exact location.

</details>
