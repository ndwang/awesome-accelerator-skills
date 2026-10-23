#!/usr/bin/env python3
"""Optional, dependency-free lookup of pinned Bmad, Tao, and PyTao sources.

SPDX-License-Identifier: GPL-3.0-only
Source files keep their upstream license and original bytes. No model, embedding
service, PDF converter, or runtime Bmad installation is required.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
from urllib.parse import quote
from urllib.request import Request, urlopen


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = Path(os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")) / "bmad-ecosystem-docs"
SHA = re.compile(r"[0-9a-f]{40}")
MAX_FILE_BYTES = 16 * 1024 * 1024


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("projects"), dict):
        raise ValueError("unsupported source manifest")
    for name, project in manifest["projects"].items():
        if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
            raise ValueError("invalid project name")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", project["repository"]):
            raise ValueError(f"invalid repository for {name}")
        if not SHA.fullmatch(project["revision"]):
            raise ValueError(f"{name} must pin a full commit SHA")
        seen = set()
        for entry in project["files"]:
            path = entry["path"]
            if not isinstance(path, str) or "\\" in path or any(part in ("", ".", "..") for part in path.split("/")):
                raise ValueError(f"invalid source path: {path!r}")
            if PurePosixPath(path).is_absolute() or path in seen:
                raise ValueError(f"invalid or duplicate source path: {path!r}")
            if not SHA.fullmatch(entry["git_blob_sha"]) or not isinstance(entry["size"], int) or not 0 <= entry["size"] <= MAX_FILE_BYTES:
                raise ValueError(f"invalid source integrity metadata: {path}")
            seen.add(path)
    return manifest


def source_url(project: dict, entry: dict, *, raw: bool = False) -> str:
    base = "https://raw.githubusercontent.com" if raw else "https://github.com"
    middle = "" if raw else "/blob"
    return f"{base}/{project['repository']}{middle}/{project['revision']}/{quote(entry['path'], safe='/')}"


def download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "bmad-ecosystem-skill/2.0"})
    with urlopen(request, timeout=30) as response:
        data = response.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("source exceeds maximum file size")
    return data


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def verified_bytes(cache: Path, entry: dict) -> bytes:
    path = cache / "objects" / entry["git_blob_sha"]
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise ValueError(f"missing cached source: {entry['path']}; run fetch") from exc
    if len(data) != entry["size"] or blob_sha(data) != entry["git_blob_sha"]:
        raise ValueError(f"cached source failed integrity check: {entry['path']}; run fetch")
    return data


def load_catalog(cache: Path) -> dict:
    path = cache / "catalog.json"
    if not path.exists():
        return {"schema_version": 1, "projects": {}}
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if catalog.get("schema_version") != 1 or not isinstance(catalog.get("projects"), dict):
        raise ValueError("invalid cache catalog; choose a new cache directory")
    return catalog


def project_names(manifest: dict, selection: str) -> list[str]:
    if selection == "all":
        return list(manifest["projects"])
    if selection not in manifest["projects"]:
        raise ValueError(f"unknown project {selection!r}; choose one of {', '.join(manifest['projects'])}")
    return [selection]


def fetch(manifest: dict, cache: Path, names: list[str], *, checkout: Path | None = None, fetcher=download) -> int:
    """Fetch all selected inputs before atomically publishing their catalog.

    A failed fetch may leave verified immutable objects, but it never advertises
    an incomplete project as ready. Existing catalog entries remain usable.
    """
    catalog = load_catalog(cache)
    if checkout is not None:
        checkout = checkout.resolve()
        repositories = {manifest["projects"][name]["repository"] for name in names}
        if len(repositories) != 1:
            raise ValueError("--checkout must refer to one repository; select bmad, tao, or pytao")

    def obtain(item: tuple[dict, dict]) -> None:
        project, entry = item
        try:
            verified_bytes(cache, entry)
            return
        except ValueError:
            pass
        if checkout is None:
            data = fetcher(source_url(project, entry, raw=True))
        else:
            path = (checkout / entry["path"]).resolve()
            if not path.is_relative_to(checkout):
                raise ValueError(f"source leaves checkout: {entry['path']}")
            data = path.read_bytes()
        if len(data) != entry["size"] or blob_sha(data) != entry["git_blob_sha"]:
            raise ValueError(f"source does not match pinned Git blob: {entry['path']}")
        atomic_write(cache / "objects" / entry["git_blob_sha"], data)

    items = [(manifest["projects"][name], entry) for name in names for entry in manifest["projects"][name]["files"]]
    with ThreadPoolExecutor(max_workers=6) as executor:
        list(executor.map(obtain, items))
    for name in names:
        catalog["projects"][name] = manifest["projects"][name]
    atomic_write(cache / "catalog.json", (json.dumps(catalog, indent=2) + "\n").encode("utf-8"))
    return len(items)


def require_project(manifest: dict, cache: Path, name: str) -> dict:
    project = manifest["projects"][name]
    if load_catalog(cache)["projects"].get(name) != project:
        raise ValueError(f"cache for {name} does not match sources.lock.json; run fetch --project {name}")
    return project


def text_view(path: str, data: bytes, *, raw: bool = False) -> str:
    text = data.decode("utf-8")
    if raw or not path.endswith(".ipynb"):
        return text
    notebook = json.loads(text)
    lines = ["Notebook input view: line numbers refer to this view, not notebook JSON.", "Outputs and execution counts are omitted; they are not current runtime evidence.", ""]
    for index, cell in enumerate(notebook.get("cells", []), start=1):
        source = cell.get("source", [])
        if isinstance(source, list):
            source = "".join(source)
        lines.extend([f"### Cell {index} ({cell.get('cell_type', 'unknown')})", source, ""])
    return "\n".join(lines)


def read_lines(manifest: dict, cache: Path, name: str, path: str, *, raw: bool = False) -> tuple[dict, list[str]]:
    project = require_project(manifest, cache, name)
    entry = next((entry for entry in project["files"] if entry["path"] == path), None)
    if entry is None:
        raise ValueError(f"source path is not in the manifest: {path}; use list --project {name}")
    data = verified_bytes(cache, entry)
    return entry, text_view(path, data, raw=raw).splitlines()


def search(manifest: dict, cache: Path, names: list[str], query: str, *, regex: bool = False):
    if not query:
        raise ValueError("search query must not be empty")
    pattern = re.compile(query if regex else re.escape(query), re.IGNORECASE)
    for name in names:
        project = require_project(manifest, cache, name)
        for entry in project["files"]:
            lines = text_view(entry["path"], verified_bytes(cache, entry)).splitlines()
            for number, line in enumerate(lines, start=1):
                if pattern.search(line):
                    yield name, entry, number, line


def positive(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE, help="external source cache directory")
    parser.add_argument("--manifest", type=Path, default=SKILL_DIR / "sources.lock.json")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("sources", help="show pinned upstream repositories and documentation URLs")
    listing = commands.add_parser("list", help="list source paths in the manifest; no network required")
    listing.add_argument("--project", default="all")
    fetching = commands.add_parser("fetch", help="fetch and verify pinned inputs (or reuse verified cached copies)")
    fetching.add_argument("--project", default="all")
    fetching.add_argument("--checkout", type=Path, help="read source bytes from a checkout instead of the network")
    searching = commands.add_parser("search", help="search verified cached source text or notebook inputs")
    searching.add_argument("query")
    searching.add_argument("--project", default="all")
    searching.add_argument("--regex", action="store_true")
    searching.add_argument("--limit", type=positive, default=20)
    reading = commands.add_parser("read", help="read a source window with upstream provenance")
    reading.add_argument("project")
    reading.add_argument("path")
    reading.add_argument("--start", type=positive, default=1)
    reading.add_argument("--lines", type=positive, default=100)
    reading.add_argument("--raw", action="store_true", help="show raw notebook JSON instead of cell inputs")
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        names = project_names(manifest, getattr(args, "project", "all"))
        if args.command == "sources":
            for name, project in manifest["projects"].items():
                print(f"{name}: {project['repository']} @ {project['revision']} ({len(project['files'])} files)")
                print(f"  {project['documentation_url']}")
            print("These are source snapshots; compare with the installed runtime version before use.")
        elif args.command == "list":
            for name in names:
                for entry in manifest["projects"][name]["files"]:
                    print(f"{name}\t{entry['path']}\t{entry['size']} bytes")
        elif args.command == "fetch":
            count = fetch(manifest, args.cache, names, checkout=args.checkout)
            print(f"Verified {count} source entries for {', '.join(names)} in {args.cache.resolve()}")
        elif args.command == "search":
            # Verify catalog coverage before yielding any hits or applying the limit.
            for name in names:
                require_project(manifest, args.cache, name)
            print(f"Searching pinned sources: {', '.join(names)}. Notebook lines refer to input views.")
            found = 0
            for name, entry, number, line in search(manifest, args.cache, names, args.query, regex=args.regex):
                print(f"{name}:{entry['path']}:{number}: {line.strip()}")
                print(f"  {source_url(manifest['projects'][name], entry)}")
                found += 1
                if found >= args.limit:
                    print(f"Stopped at {args.limit} hits; increase --limit or narrow the query.")
                    break
            if not found:
                print("No matching lines in the selected pinned sources.")
        elif args.command == "read":
            if args.project == "all":
                raise ValueError("read requires one project")
            entry, lines = read_lines(manifest, args.cache, args.project, args.path, raw=args.raw)
            if args.start > len(lines):
                raise ValueError(f"start line exceeds document length ({len(lines)} lines)")
            print(source_url(manifest["projects"][args.project], entry))
            if args.path.endswith(".ipynb") and not args.raw:
                print("Notebook input view; line numbers below are view lines, not JSON source lines.")
            for index in range(args.start - 1, min(args.start - 1 + args.lines, len(lines))):
                print(f"{index + 1:5d}: {lines[index]}")
        return 0
    except (OSError, ValueError, KeyError, TypeError, re.error) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
