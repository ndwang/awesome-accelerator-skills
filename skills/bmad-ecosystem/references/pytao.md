# PyTao: Python access to Tao

Use PyTao to control Tao and extract its calculated data from Python. The lattice physics and coordinate conventions remain Bmad's; the commands and state model remain Tao's. Read [bmad.md](bmad.md) and [tao.md](tao.md) when those definitions are involved.

## Inspect the installed interface first

Prefer the user's working Python environment. Record Python, `pytao` package version, the loaded Tao library path when available, and Tao's reported version. Verify both Python import and native-library initialization: installing the Python package alone does not demonstrate that its required Tao shared library is available. See the version-matched installation documentation. [Pinned installation source][installation]

Use Python introspection before assuming that a method or keyword exists:

```python
import inspect
from importlib.metadata import version
from pytao import Tao

print(version("pytao"))
print(inspect.signature(Tao))
print(inspect.signature(Tao.ele_twiss))
```

Inspect that installation's docstrings or source for a changed return schema. The [published documentation](https://bmad-sim.github.io/pytao/) and pinned sources below are useful references, but may describe a different version. Read the required files directly or use the optional helper in [documentation.md](documentation.md).

## Start with a small, headless calculation

From a working directory containing the copied FODO `tao.init` and lattice:

```python
from pytao import Tao

tao = Tao(init_file="tao.init", noplot=True)
print("\n".join(tao.cmd("show lattice")))
head = tao.ele_head("1@0>>END", which="model")
twiss = tao.ele_twiss("1@0>>END", which="model")
print(head)
print(twiss)
```

These constructor and method forms are present in the pinned [Tao class][tao_source] and [generated command interface][interface]. Inspect the returned keys before selecting a quantity. Keep the universe, branch, and lattice state explicit when a calculation has several of them.

Use `noplot=True` for headless execution. Preserve startup scripts when reproducing an existing calculation; if one requires plotting, inspect it and make a deliberate headless variant. Avoid setting `quiet=True` merely to reduce logs: the pinned [usage documentation][usage] warns that it can interfere with PyTao behavior.

## Distinguish the API layers

| Interface | Result and appropriate use |
| --- | --- |
| `tao.cmd("...")` | A list of text lines; useful for commands and human-readable diagnostics. |
| `tao.ele_head(...)`, `tao.ele_twiss(...)`, `tao.ele_gen_attribs(...)` | Parsed dictionaries in the pinned interface; inspect keys and meanings for the installed version. |
| `tao.evaluate(expression)` | A numerical result that can be an array even for one value; validate its size before scalar conversion. |
| `tao.lat_list(...)` | Selected lattice quantities; numerical array output is useful when preserving full floating-point precision. |
| `tao.cmd_real(...)`, `tao.cmd_integer(...)` | Native numerical buffers; use only commands documented to populate the corresponding buffer. |
| Raw `pipe ...` through `cmd` | Tao protocol text; parse according to that specific subcommand's documented schema. |

Prefer an existing parsed method over splitting `show lattice` columns. `cmd_real` is not a general text-to-number conversion function. A parser mismatch should lead to inspection of the installed interface and raw response, rather than assumptions about older key names. [Core implementation][core] and [command interface][interface]

Leave normal exception raising enabled. Capture the failing command and diagnostic when a Tao command fails; suppress an error only for a specific documented recovery and report it. Initialization and shared-library failures are different from invalid lattice physics.

## Isolate independent Tao calculations

Use a supported `SubprocessTao` for independent sessions or worker processes, and close each session reliably. The pinned implementation supports a context manager and an explicit working directory:

```python
from pytao import SubprocessTao

with SubprocessTao(init_file="tao.init", cwd="/path/to/run", noplot=True) as tao:
    optics = tao.ele_twiss("1@0>>END", which="model")
```

Check this constructor against the installed version. Give concurrent runs separate working/output directories. Avoid assuming that separate in-process Python objects provide independent native state or thread-safe access. See [usage][usage] and the [subprocess implementation][subproc].

## Scan or optimize without leaving hidden state

Record the original knob values and calculation flags. For every sample, set the intended values, ensure calculation has occurred, and check that the returned observable is finite and physically valid. Restore values and flags in `finally`, then verify restoration. If restoring fails, report that failure and discard the session.

Choose a getter with enough precision for restoration. Parsed floating-point values can still originate in rounded text output; use a suitable numerical-array query when exact round-trip restoration matters. [Command interface][interface]

Use the bundled [quadrupole scan](../scripts/scan_quadrupole.py) as a small example; inspect `--help` for its actual interface. For an expensive lattice, batch updates only after this simple path works. Include rejected points and their failure reasons in a scan report instead of silently interpolating or replacing them.

[installation]: https://github.com/bmad-sim/pytao/blob/c22d07778faf2b70f28a914362e215e5bb9ced25/docs/installation.md
[usage]: https://github.com/bmad-sim/pytao/blob/c22d07778faf2b70f28a914362e215e5bb9ced25/docs/usage.md
[tao_source]: https://github.com/bmad-sim/pytao/blob/c22d07778faf2b70f28a914362e215e5bb9ced25/pytao/tao.py
[core]: https://github.com/bmad-sim/pytao/blob/c22d07778faf2b70f28a914362e215e5bb9ced25/pytao/core.py
[interface]: https://github.com/bmad-sim/pytao/blob/c22d07778faf2b70f28a914362e215e5bb9ced25/pytao/interface_commands.py
[subproc]: https://github.com/bmad-sim/pytao/blob/c22d07778faf2b70f28a914362e215e5bb9ced25/pytao/subproc.py
