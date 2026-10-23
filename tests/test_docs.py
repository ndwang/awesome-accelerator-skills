"""Source provenance and offline lookup behavior for the optional docs helper."""

from contextlib import redirect_stdout
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "bmad-ecosystem" / "scripts" / "docs.py"
SPEC = importlib.util.spec_from_file_location("bmad_skill_docs", SCRIPT)
docs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(docs)


class DocumentationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.cache = self.directory / "cache"
        self.source = b"\\section{Coordinates}\nCanonical momentum uses the reference momentum.\n"
        self.notebook = json.dumps({"cells": [
            {"cell_type": "markdown", "source": ["# Example\n", "Cell instructions\n"]},
            {"cell_type": "code", "source": ["tao.cmd(\"show version\")\n"], "execution_count": 9,
             "outputs": [{"output_type": "stream", "text": ["fabricated runtime result\n"]}]},
        ]}).encode()
        self.files = {"docs/coordinates.tex": self.source, "docs/example.ipynb": self.notebook}
        self.manifest = {"schema_version": 1, "projects": {"bmad": {
            "repository": "example/bmad", "revision": "1" * 40,
            "documentation_url": "https://example.invalid/docs",
            "files": [{"path": path, "git_blob_sha": docs.blob_sha(data), "size": len(data)}
                      for path, data in self.files.items()],
        }}}
        self.manifest_path = self.directory / "sources.lock.json"
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")

    def fetcher(self, url):
        return self.files[url.split("/" + "1" * 40 + "/", 1)[1]]

    def populate(self):
        return docs.fetch(self.manifest, self.cache, ["bmad"], fetcher=self.fetcher)

    def test_git_object_hash_matches_git(self):
        self.assertEqual(docs.blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_checkout_preserves_original_source_bytes_and_supports_offline_lookup(self):
        checkout = self.directory / "checkout"
        for path, data in self.files.items():
            target = checkout / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        def unavailable(url):
            raise AssertionError("network must not be used")
        docs.fetch(self.manifest, self.cache, ["bmad"], checkout=checkout, fetcher=unavailable)
        for entry in self.manifest["projects"]["bmad"]["files"]:
            self.assertEqual(docs.verified_bytes(self.cache, entry), self.files[entry["path"]])
        _, lines = docs.read_lines(self.manifest, self.cache, "bmad", "docs/coordinates.tex")
        self.assertIn("Canonical momentum", lines[1])
        hits = list(docs.search(self.manifest, self.cache, ["bmad"], "canonical momentum"))
        self.assertEqual([(hit[1]["path"], hit[2]) for hit in hits], [("docs/coordinates.tex", 2)])

    def test_warm_fetch_does_not_require_network(self):
        self.populate()
        def unavailable(url):
            raise AssertionError("network must not be used for a verified object")
        self.assertEqual(docs.fetch(self.manifest, self.cache, ["bmad"], fetcher=unavailable), 2)

    def test_incomplete_update_keeps_previous_active_catalog(self):
        self.populate()
        previous = (self.cache / "catalog.json").read_bytes()
        updated = deepcopy(self.manifest)
        addition = b"New source content\n"
        updated["projects"]["bmad"]["files"].append({"path": "docs/new.tex", "git_blob_sha": docs.blob_sha(addition), "size": len(addition)})
        with self.assertRaisesRegex(ValueError, "does not match pinned"):
            docs.fetch(updated, self.cache, ["bmad"], fetcher=lambda url: b"incorrect download")
        self.assertEqual((self.cache / "catalog.json").read_bytes(), previous)
        docs.read_lines(self.manifest, self.cache, "bmad", "docs/coordinates.tex")

    def test_corrupted_cache_is_detected_and_fetch_repairs_it(self):
        self.populate()
        entry = self.manifest["projects"]["bmad"]["files"][0]
        (self.cache / "objects" / entry["git_blob_sha"]).write_bytes(b"misleading replacement")
        with self.assertRaisesRegex(ValueError, "integrity check"):
            docs.read_lines(self.manifest, self.cache, "bmad", entry["path"])
        self.populate()
        self.assertEqual(docs.verified_bytes(self.cache, entry), self.source)

    def test_cache_cannot_silently_supply_a_different_revision(self):
        self.populate()
        changed = deepcopy(self.manifest)
        changed["projects"]["bmad"]["revision"] = "2" * 40
        with self.assertRaisesRegex(ValueError, "does not match sources.lock"):
            docs.read_lines(changed, self.cache, "bmad", "docs/coordinates.tex")

    def test_notebook_search_indexes_cell_inputs_and_omits_stale_outputs(self):
        self.populate()
        self.assertEqual(list(docs.search(self.manifest, self.cache, ["bmad"], "fabricated runtime result")), [])
        hits = list(docs.search(self.manifest, self.cache, ["bmad"], "show version"))
        self.assertEqual(len(hits), 1)
        _, lines = docs.read_lines(self.manifest, self.cache, "bmad", "docs/example.ipynb")
        self.assertIn("line numbers refer to this view", lines[0])
        _, raw = docs.read_lines(self.manifest, self.cache, "bmad", "docs/example.ipynb", raw=True)
        self.assertIn("fabricated runtime result", "\n".join(raw))

    def test_literal_query_does_not_act_as_regex(self):
        self.populate()
        self.assertEqual(list(docs.search(self.manifest, self.cache, ["bmad"], "Canonical.*momentum")), [])
        self.assertEqual(len(list(docs.search(self.manifest, self.cache, ["bmad"], "Canonical.*momentum", regex=True))), 1)

    def test_manifest_rejects_paths_that_escape_a_checkout(self):
        changed = deepcopy(self.manifest)
        changed["projects"]["bmad"]["files"][0]["path"] = "../outside.tex"
        self.manifest_path.write_text(json.dumps(changed), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid source path"):
            docs.load_manifest(self.manifest_path)

    def test_read_command_reports_provenance_and_exact_window(self):
        self.populate()
        output = io.StringIO()
        with redirect_stdout(output):
            status = docs.main(["--manifest", str(self.manifest_path), "--cache", str(self.cache),
                                "read", "bmad", "docs/coordinates.tex", "--start", "2", "--lines", "1"])
        self.assertEqual(status, 0)
        self.assertIn("https://github.com/example/bmad/blob/" + "1" * 40, output.getvalue())
        self.assertIn("    2: Canonical momentum", output.getvalue())
        self.assertNotIn("section{", output.getvalue())

    def test_source_manifest_is_found_after_the_skill_is_relocated(self):
        relocated = self.directory / "copied-skill"
        (relocated / "scripts").mkdir(parents=True)
        shutil.copyfile(SCRIPT, relocated / "scripts" / "docs.py")
        shutil.copyfile(self.manifest_path, relocated / "sources.lock.json")
        result = subprocess.run([sys.executable, str(relocated / "scripts" / "docs.py"), "sources"],
                                cwd=self.directory, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("example/bmad", result.stdout)


if __name__ == "__main__":
    unittest.main()
