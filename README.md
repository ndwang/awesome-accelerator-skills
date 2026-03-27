# Awesome Accelerator Skills

AI agent skills for the [Bmad](https://www.classe.cornell.edu/bmad) accelerator simulation
toolkit and the [Tao](https://www.classe.cornell.edu/bmad/tao.html) program. The skills are
plain markdown files organized with progressive disclosure -- a concise main file plus detailed
reference files loaded on demand. This makes them portable across agent harnesses.

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
- **references/** -- 9 reference files covering commands, initialization, data, variables,
  optimization, plotting, pipe interface, and single-mode operation

## Installation

### Claude Code

**As a plugin** (recommended for sharing):
```bash
claude --plugin-dir /path/to/awesome-accelerator-skills
```

**As project-level skills** (shared via git):
```bash
cp -r skills/bmad /path/to/project/.claude/skills/
cp -r skills/tao /path/to/project/.claude/skills/
```

**As personal skills** (all your projects):
```bash
cp -r skills/bmad ~/.claude/skills/
cp -r skills/tao ~/.claude/skills/
```

Claude Code automatically loads SKILL.md when the skill triggers and reads reference files
on demand via the pointers in SKILL.md.

### Cursor

Add the SKILL.md files as project rules. In your project root:

```bash
mkdir -p .cursor/rules
cp skills/bmad/SKILL.md .cursor/rules/bmad.md
cp skills/tao/SKILL.md .cursor/rules/tao.md
```

For reference files, either append them to the rule files or instruct Cursor to read them
from the `skills/` directory when needed. You can also add them as documentation context
in `.cursor/rules/` with filenames that indicate when to load them.

### Windsurf

Place the SKILL.md files in your project's `.windsurfrules` or global rules:

```bash
# Project-level
cp skills/bmad/SKILL.md .windsurfrules/bmad.md
cp skills/tao/SKILL.md .windsurfrules/tao.md
```

Reference files can live in the repo; Windsurf's Cascade will read them when directed
by the pointers in the main skill files.

### Cline / Roo Code

Add SKILL.md content to `.clinerules` or custom instructions:

```bash
cp skills/bmad/SKILL.md .clinerules/bmad.md
cp skills/tao/SKILL.md .clinerules/tao.md
```

Place the `skills/` directory in the project root so the agent can read reference files
when the SKILL.md pointers direct it to.

### OpenAI Codex CLI

Use SKILL.md as a project-level instruction file:

```bash
# Copy into the project's instructions directory
cp skills/bmad/SKILL.md codex-instructions/bmad.md
cp skills/tao/SKILL.md codex-instructions/tao.md
```

Reference as custom instructions via `AGENTS.md` or the `--instructions` flag. The agent
can read reference files from the repo when needed.

### ChatGPT / Custom GPTs

Paste the contents of SKILL.md into the system instructions (Custom Instructions or GPT
configuration). For reference files, upload them as knowledge files -- ChatGPT will
retrieve relevant sections automatically.

### LangChain / LlamaIndex / Custom RAG

Use the skill files as retrieval documents:

```python
# Load all skill content as documents
from pathlib import Path

docs = []
for md_file in Path("skills").rglob("*.md"):
    docs.append({
        "content": md_file.read_text(),
        "metadata": {"source": str(md_file)}
    })
# Index with your vector store of choice
```

For simpler setups, include SKILL.md directly in the system prompt and load reference
files into a retrieval tool the agent can query.

### Raw API Calls (Anthropic, OpenAI, etc.)

Include SKILL.md in the system message. Provide reference files either by appending them
when the context is relevant, or by making them available as tool results:

```python
system_prompt = Path("skills/bmad/SKILL.md").read_text()
# Strip the YAML frontmatter (lines between --- markers) if the API doesn't use it
```

### General Guidance

The skill files are plain markdown. To use them with any agent:

1. **Load SKILL.md into the system prompt or instructions** -- this gives the agent
   working knowledge of Bmad/Tao (~400-450 lines each)
2. **Make reference files accessible** -- either in the prompt, as retrievable documents,
   or as files the agent can read on demand
3. **The YAML frontmatter** (`name`, `description`) is Claude Code-specific metadata for
   triggering. Other harnesses can ignore it or strip it
4. **The "When to Load" pointers** in SKILL.md tell any agent when to consult each
   reference file -- this progressive disclosure pattern works across harnesses

## Source Documentation

The `docs/` directory contains the original Bmad LaTeX documentation used to generate these
skills. The skills cover Parts I (Language Reference) and II (Conventions and Physics) of the
Bmad manual.

## License

The Bmad documentation is maintained by the Cornell Laboratory for Accelerator-based Sciences
and Education (CLASSE). See `docs/bmad/Copyright` for details.
