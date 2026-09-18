"""Unit tests for deterministic solver readiness evidence binding."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from generation import readiness

REQUIRED = ["satisfaction", "changed_instances", "malformed_output", "empty_output", "timeout_cleanup",
            "isolation", "missing_image", "minimization", "maximization", "enumeration"]

# Stand-ins for a real solvers/<id>/readiness_test.py, which drives the
# evaluator against containers and exits nonzero when any check fails.
ALL_PASS = '''import json
print(json.dumps({name: True for name in %r}))
''' % (REQUIRED,)

ONE_FAILS = '''import json, sys
results = {name: True for name in %r}
results["isolation"] = False
print(json.dumps(results))
sys.exit(1)
''' % (REQUIRED,)


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        folder = self.root / "solvers" / "demo"
        folder.mkdir(parents=True)
        (folder / "metadata.yaml").write_text('{"id":"demo","image":"demo:image","enumeration":true}', encoding="utf-8")
        (folder / "run.py").write_text("runner", encoding="utf-8")
        (folder / "Dockerfile").write_text("FROM scratch", encoding="utf-8")
        self.script = folder / readiness.CHECK_SCRIPT
        self.write_script(ALL_PASS)
        self.evidence = self.root / "evidence.txt"; self.evidence.write_text("passed", encoding="utf-8")
        self.metadata = {"id": "demo", "image": "demo:image", "enumeration": True}
        self.patch = patch.multiple(readiness, ROOT=self.root,
                                    integration=lambda solver: self.metadata if solver == "demo" else None,
                                    image_identity=lambda metadata: "sha256:image")
        self.patch.start()

    def tearDown(self):
        self.patch.stop(); self.temp.cleanup()

    def write_script(self, source):
        self.script.write_text(source, encoding="utf-8")

    def report(self, names=None):
        required = names or {"satisfaction", "changed_instances", "malformed_output", "empty_output", "timeout_cleanup",
                             "isolation", "missing_image", "minimization", "maximization", "enumeration"}
        return {"image_id": "sha256:image", "tests": [{"name": name, "passed": True, "evidence": [str(self.evidence)]}
                                                            for name in sorted(required)]}

    def write_report(self, value):
        path = self.root / "report.json"; path.write_text(json.dumps(value), encoding="utf-8"); return path

    def test_check_and_verify_full_current_evidence(self):
        record_path = self.root / "record.json"
        record = readiness.check("demo", self.write_report(self.report()), record_path)
        self.assertTrue(record["accepted"])
        self.assertEqual(readiness.verify("demo", record_path)["image_id"], "sha256:image")

    def test_rejects_missing_duplicate_failed_and_empty_evidence(self):
        missing = self.report({"satisfaction"})
        with self.assertRaises(readiness.ReadinessError): readiness.check("demo", self.write_report(missing), self.root / "a.json")
        duplicate = self.report(); duplicate["tests"].append(duplicate["tests"][0])
        with self.assertRaises(readiness.ReadinessError): readiness.check("demo", self.write_report(duplicate), self.root / "b.json")
        failed = self.report(); failed["tests"][0]["passed"] = False
        with self.assertRaises(readiness.ReadinessError): readiness.check("demo", self.write_report(failed), self.root / "c.json")
        empty = self.report(); empty["tests"][0]["evidence"] = []
        with self.assertRaises(readiness.ReadinessError): readiness.check("demo", self.write_report(empty), self.root / "d.json")

    def test_capability_specific_requirements(self):
        self.metadata = {"id": "demo", "image": "demo:image", "enumeration": False, "optimization": False, "compilation": True}
        required = {"satisfaction", "changed_instances", "malformed_output", "empty_output", "timeout_cleanup",
                    "isolation", "missing_image", "unsupported_optimization", "unsupported_enumeration", "compilation_error"}
        readiness.check("demo", self.write_report(self.report(required)), self.root / "record.json")

    def test_verify_detects_changed_evidence_and_runner(self):
        record_path = self.root / "record.json"
        readiness.check("demo", self.write_report(self.report()), record_path)
        self.evidence.write_text("changed", encoding="utf-8")
        with self.assertRaises(readiness.ReadinessError): readiness.verify("demo", record_path)
        self.evidence.write_text("passed", encoding="utf-8")
        (self.root / "solvers" / "demo" / "run.py").write_text("changed", encoding="utf-8")
        with self.assertRaises(readiness.ReadinessError): readiness.verify("demo", record_path)

    def test_renaming_or_retagging_leaves_the_record_valid(self):
        """A display name and a paradigm tag are read by the catalogue, not by
        the container. Hashing metadata.yaml whole once invalidated all nine
        records over a rename, so the record pins behaviour only."""
        record_path = self.root / "record.json"
        readiness.check("demo", self.write_report(self.report()), record_path)
        for field, value in (("name", "Renamed"), ("paradigms", ["cp", "mip"])):
            with self.subTest(field=field):
                self.metadata[field] = value
                self.assertTrue(readiness.verify("demo", record_path)["accepted"])

    def test_a_behavioural_metadata_change_still_invalidates_the_record(self):
        record_path = self.root / "record.json"
        readiness.check("demo", self.write_report(self.report()), record_path)
        for field, value in (("extension", ".zzz"), ("image", "other:image"),
                             ("instance_binding", "rectangular_uniform")):
            with self.subTest(field=field):
                original = self.metadata.get(field)
                self.metadata[field] = value
                with self.assertRaisesRegex(readiness.ReadinessError, "changed since readiness check"):
                    readiness.verify("demo", record_path)
                if original is None:
                    del self.metadata[field]
                else:
                    self.metadata[field] = original

    def test_checks_are_executed_rather_than_asserted(self):
        """The report is built from the script's real output, not from a claim."""
        report = readiness.run_checks("demo", self.root / "evidence")
        record = readiness.check("demo", report, self.root / "record.json")
        self.assertEqual({item["name"] for item in record["tests"]}, set(REQUIRED))
        self.assertTrue((self.root / "evidence" / "readiness-result.json").is_file())
        self.assertIn("checks", record["integration_files"])

    def test_checks_can_be_rerun_after_a_repair(self):
        """A failed run must not block the retry that fixes it."""
        self.write_script(ONE_FAILS)
        evidence = self.root / "evidence"
        with self.assertRaises(readiness.ReadinessError):
            readiness.run_checks("demo", evidence)
        self.write_script(ALL_PASS)
        report = readiness.run_checks("demo", evidence)
        self.assertTrue(readiness.check("demo", report, self.root / "record.json")["accepted"])

    def test_a_failing_check_script_cannot_produce_a_record(self):
        self.write_script(ONE_FAILS)
        with self.assertRaisesRegex(readiness.ReadinessError, "exited 1"):
            readiness.run_checks("demo", self.root / "failed")
        # The output is still kept, so the failure can be diagnosed.
        self.assertIn("isolation", (self.root / "failed" / "readiness-result.json").read_text(encoding="utf-8"))
        self.assertFalse((self.root / "failed" / "readiness-report.json").exists())

    def test_editing_the_check_script_invalidates_the_record(self):
        record_path = self.root / "record.json"
        readiness.check("demo", readiness.run_checks("demo", self.root / "evidence"), record_path)
        self.write_script(ALL_PASS + "# quietly weakened\n")
        with self.assertRaisesRegex(readiness.ReadinessError, "changed since readiness check"):
            readiness.verify("demo", record_path)

    def test_an_integration_without_a_check_script_is_not_ready(self):
        self.script.unlink()
        with self.assertRaisesRegex(readiness.ReadinessError, readiness.CHECK_SCRIPT):
            readiness.run_checks("demo", self.root / "evidence")

    def test_report_image_must_match_actual(self):
        report = self.report(); report["image_id"] = "sha256:wrong"
        with self.assertRaises(readiness.ReadinessError): readiness.check("demo", self.write_report(report), self.root / "record.json")


    def test_a_record_verifies_after_the_repository_moves(self):
        """Records are committed, so they must survive a checkout at another path.

        Absolute evidence paths would pin every record to the machine that
        produced it, leaving a fresh clone with no usable integration at all.
        """
        record = self.root / "solvers" / "demo" / "readiness.json"
        readiness.check("demo", self.write_report(self.report()), record)
        stored = json.loads(record.read_text(encoding="utf-8"))
        paths = {evidence["path"] for test in stored["tests"] for evidence in test["evidence"]}
        self.assertEqual(paths, {"evidence.txt"})
        with tempfile.TemporaryDirectory() as elsewhere:
            moved = Path(elsewhere) / "checkout"
            shutil.copytree(self.root, moved)
            with patch.object(readiness, "ROOT", moved):
                readiness.verify("demo", moved / "solvers" / "demo" / "readiness.json")

    def test_absolute_evidence_is_refused_on_both_sides(self):
        with tempfile.TemporaryDirectory() as outside:
            stray = Path(outside) / "evidence.txt"
            stray.write_text("passed", encoding="utf-8")
            report = self.report()
            for test in report["tests"]:
                test["evidence"] = [str(stray)]
            with self.assertRaisesRegex(readiness.ReadinessError, "inside the repository"):
                readiness.check("demo", self.write_report(report), self.root / "record.json")
        record = self.root / "solvers" / "demo" / "readiness.json"
        readiness.check("demo", self.write_report(self.report()), record)
        stored = json.loads(record.read_text(encoding="utf-8"))
        stored["tests"][0]["evidence"][0]["path"] = str(self.evidence)
        record.write_text(json.dumps(stored), encoding="utf-8")
        with self.assertRaisesRegex(readiness.ReadinessError, "repository-relative"):
            readiness.verify("demo", record)

if __name__ == "__main__":
    unittest.main()
