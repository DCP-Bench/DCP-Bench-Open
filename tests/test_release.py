from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from generation import release

SKILL = ("---\nname: demo-python\ndescription: Demo, a Python solver. Use when modelling with Demo.\n"
         "license: Apache-2.0\nmetadata:\n  domain: constraint-programming\n---\n\n# Demo\n\nModel with it.\n")
SOURCES = "# Sources\n\nTested with Demo 1.2.3 on Python 3.12.\n\n- <https://example.org/demo>\n"


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        patcher = patch.object(release, "ROOT", self.root)
        patcher.start(); self.addCleanup(patcher.stop)
        self.source = self.root / "solvers/demo_python/skills/demo-python"
        self.write("SKILL.md", SKILL)
        self.write("sources.md", SOURCES)
        self.write("assets/example/model.py", "print('ok')\n")
        (self.root / "solvers/demo_python/readiness.json").write_text(json.dumps({"image_id": "sha256:abc"}))
        (self.root / "skills/.claude-plugin").mkdir(parents=True)
        (self.root / "skills/README.md").write_text("# Skills\n\n## Catalog\n\n| add-solver |\n")
        (self.root / release.MARKETPLACE).write_text(json.dumps(
            {"name": "m", "plugins": [{"name": "meta", "source": "./", "skills": ["./add-solver"]}]}))
        for command in (["init", "-q"], ["config", "user.name", "Tester"], ["config", "user.email", "t@example.org"]):
            self.git(*command)
        self.commit()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True,
                              text=True).stdout.strip()

    def write(self, relative, text):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "change")

    def publish(self, **kwargs):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return release.publish("demo_python", kwargs.pop("message", "First release"), **kwargs)

    def ledger(self):
        return json.loads((self.root / release.LEDGER).read_text())["skills"]["demo-python"]

    def status(self):
        output = io.StringIO()
        with redirect_stdout(output):
            problems = release.status()
        return output.getvalue(), problems

    def test_first_release_copies_records_and_registers(self):
        self.publish()
        published = self.root / "skills/solvers/demo-python"
        self.assertIn('  version: "0.1.0"', (published / "SKILL.md").read_text())
        self.assertIn("  domain: constraint-programming", (published / "SKILL.md").read_text())
        entry = self.ledger()
        self.assertEqual(entry["version"], "0.1.0")
        self.assertEqual(entry["source"]["commit"], self.git("rev-parse", "HEAD"))
        self.assertEqual(entry["source"]["tree"], self.git("rev-parse", "HEAD:solvers/demo_python/skills/demo-python"))
        self.assertFalse(entry["source"]["dirty"])
        self.assertEqual(entry["content_digest"], release.digest(published))
        self.assertEqual(entry["evidence"]["readiness"]["image_id"], "sha256:abc")
        self.assertEqual(entry["evidence"]["tested_with"], "Tested with Demo 1.2.3 on Python 3.12.")
        plugins = json.loads((self.root / release.MARKETPLACE).read_text())["plugins"]
        self.assertEqual([item["name"] for item in plugins], ["meta", "solvers"])
        self.assertEqual((plugins[1]["source"], plugins[1]["skills"]), ("./solvers", ["./demo-python"]))
        self.assertNotIn("version", plugins[1])
        self.assertIn("| `demo-python` | 0.1.0 |", (self.root / "skills/README.md").read_text())
        self.assertIn("## demo-python 0.1.0", (self.root / release.CHANGELOG).read_text())

    def test_solver_skills_share_one_plugin(self):
        marketplace = self.root / release.MARKETPLACE
        data = json.loads(marketplace.read_text())
        data["plugins"].append({"name": "old-skill", "source": "./solvers/old-skill", "skills": ["./"]})
        marketplace.write_text(json.dumps(data))
        self.publish()
        other = self.root / "solvers/other_python/skills/other-python"
        other.mkdir(parents=True)
        (other / "SKILL.md").write_text(SKILL.replace("demo-python", "other-python"))
        (other / "sources.md").write_text(SOURCES)
        self.commit()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            release.publish("other_python", "First release")
        plugins = json.loads(marketplace.read_text())["plugins"]
        self.assertEqual([item["name"] for item in plugins], ["meta", "solvers"])
        self.assertEqual(plugins[1]["skills"], ["./demo-python", "./other-python"])

    def test_digest_is_path_and_content_hash_sorted_by_path(self):
        folder = self.source
        lines = "".join(f"{path}\0{hashlib.sha256((folder / path).read_bytes()).hexdigest()}\n"
                        for path in sorted(("SKILL.md", "sources.md", "assets/example/model.py")))
        self.assertEqual(release.digest(folder), "sha256:" + hashlib.sha256(lines.encode()).hexdigest())

    def test_only_tracked_files_are_released(self):
        (self.root / ".gitignore").write_text("*.class\n")
        self.write("assets/example/Model.class", "binary")
        self.commit()
        self.publish()
        self.assertFalse((self.root / "skills/solvers/demo-python/assets/example/Model.class").exists())

    def test_dirty_source_is_refused_unless_allowed_and_then_recorded(self):
        self.write("SKILL.md", SKILL + "\nUncommitted.\n")
        with self.assertRaisesRegex(release.ReleaseError, "uncommitted"):
            self.publish()
        self.publish(allow_dirty=True)
        self.assertTrue(self.ledger()["source"]["dirty"])
        self.assertIn("Uncommitted.", (self.root / "skills/solvers/demo-python/SKILL.md").read_text())

    def test_rosetta_text_is_refused_and_nothing_written(self):
        self.write("SKILL.md", SKILL + "\nRun python -m generation.brief first.\n")
        self.commit()
        with self.assertRaisesRegex(release.ReleaseError, "Rosetta"):
            self.publish()
        self.assertFalse((self.root / release.LEDGER).exists())
        self.assertFalse((self.root / "skills/solvers").exists())

    def test_versions_bump_and_unchanged_content_is_a_no_op(self):
        self.publish()
        self.assertIsNone(self.publish(message="Again"))
        self.write("SKILL.md", SKILL + "\nMore.\n")
        self.commit()
        self.publish(message="Patch")
        self.assertEqual(self.ledger()["version"], "0.1.1")
        self.publish(message="Declare stable", bump="major")
        entry = self.ledger()
        self.assertEqual(entry["version"], "1.0.0")
        self.assertEqual([item["version"] for item in entry["history"]], ["0.1.1", "0.1.0"])
        with self.assertRaisesRegex(release.ReleaseError, "greater"):
            self.publish(message="Back", version="0.9.0")
        self.publish(message="Explicit", version="1.2.0")
        self.assertEqual(self.ledger()["version"], "1.2.0")

    def test_deleted_files_disappear_from_the_published_copy(self):
        self.publish()
        self.git("rm", "-q", "-r", "solvers/demo_python/skills/demo-python/assets")
        self.git("commit", "-q", "-m", "drop assets")
        self.publish(message="Drop assets")
        self.assertFalse((self.root / "skills/solvers/demo-python/assets").exists())

    def test_status_reports_drift_in_both_directions(self):
        output, problems = self.status()
        self.assertIn("unreleased", output)
        self.assertEqual(problems, [])
        self.publish()
        output, problems = self.status()
        self.assertIn("up to date", output)
        self.write("SKILL.md", SKILL + "\nNext.\n")
        output, problems = self.status()
        self.assertIn("source changed since release", output)
        self.assertEqual(problems, [])
        (self.root / "skills/solvers/demo-python/SKILL.md").write_text("edited in place")
        output, problems = self.status()
        self.assertIn("published copy edited directly", output)
        self.assertEqual(problems, ["demo-python"])

    def test_withdraw_removes_the_copy_and_keeps_the_record(self):
        self.publish()
        with redirect_stdout(io.StringIO()):
            release.withdraw("demo-python", "Superseded")
        self.assertFalse((self.root / "skills/solvers/demo-python").exists())
        entry = self.ledger()
        self.assertEqual((entry["status"], entry["withdrawn_because"]), ("withdrawn", "Superseded"))
        plugins = json.loads((self.root / release.MARKETPLACE).read_text())["plugins"]
        self.assertEqual([item["name"] for item in plugins], ["meta"])
        self.assertNotIn("demo-python", (self.root / "skills/README.md").read_text())
        self.publish(message="Back")
        self.assertEqual(self.ledger()["version"], "0.1.1")


if __name__ == "__main__":
    unittest.main()
