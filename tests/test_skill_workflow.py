from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch
import sys

from generation import skills, behaviour

SOURCES = "# Sources" + chr(10) * 2 + "- <https://agentskills.io/specification>" + chr(10)


def write_sources(bundle):
    (bundle / "sources.md").write_text(SOURCES, encoding="utf-8")


class SkillWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(skills, "ROOT", self.root)
        self.patch.start(); self.addCleanup(self.patch.stop)
        self.bundle = self.root / "skills/test-skill"
        self.bundle.mkdir(parents=True)
        self.text = "---\nname: test-skill\ndescription: Test one bounded workflow.\n---\nOriginal instructions.\n"
        (self.bundle / "SKILL.md").write_text(self.text)
        (self.bundle / "evals").mkdir()
        (self.bundle / "evals/evals.json").write_text(json.dumps({"schema_version": 1, "skill_name": "test-skill", "evals": [
            {"id": "tiny", "prompt": "Test something.", "expected_output": "Evidence", "prerequisites": [],
             "evidence_required": ["output"], "assertions": [{"id": "done", "requirement": "Output exists"}]}]}))
        write_sources(self.bundle)
        self.run = self.root / "generation/runs/run"
        self.run.mkdir(parents=True)
        (self.run / "run.json").write_text("{}")

    def candidate(self, suffix="Correction"):
        candidate = self.root / "working/test-skill"
        candidate.mkdir(parents=True)
        (candidate / "SKILL.md").write_text(self.text + suffix)
        import shutil
        shutil.copytree(self.bundle / "evals", candidate / "evals")
        shutil.copy2(self.bundle / "sources.md", candidate / "sources.md")
        return candidate

    def checks(self, expression):
        path = self.root / "checks.json"
        path.write_text(json.dumps([{"argv": [sys.executable, "-c", expression, "{skill}"], "timeout": 10}]))
        return path

    def test_format_and_portability(self):
        self.assertEqual(skills.validate(self.bundle)["name"], "test-skill")
        (self.bundle / "SKILL.md").write_text(self.text + "[escape](../../missing.md)")
        with self.assertRaises(ValueError): skills.validate(self.bundle)

    def test_bundle_hashes_cover_every_file(self):
        """Attempt snapshots rely on these hashes, so nothing may be skipped."""
        expected = {"SKILL.md", "evals/evals.json", "sources.md"}
        self.assertEqual(set(skills.hashes(self.bundle)), expected)
        (self.bundle / "SKILL.md").write_text(self.text + "Edit")
        self.assertNotEqual(skills.hashes(self.bundle)["SKILL.md"], skills.hashes(self.candidate())["SKILL.md"])

    def test_regression_rejects_bad_skill_update(self):
        proposal = skills.propose("run", self.bundle, self.candidate("Skip evaluation"), "observed failure at run/log")
        checks = self.checks("import pathlib,sys; assert 'Skip evaluation' not in (pathlib.Path(sys.argv[1])/'SKILL.md').read_text()")
        self.assertEqual(skills.check_proposal(proposal, checks)["status"], "rejected")
        with self.assertRaises(ValueError): skills.apply(proposal)
        self.assertEqual((self.bundle / "SKILL.md").read_text(), self.text)

    def test_apply_requires_unchanged_evidence_and_base(self):
        proposal = skills.propose("run", self.bundle, self.candidate(), "API correction reproducer")
        checks = self.checks("import pathlib,sys; assert (pathlib.Path(sys.argv[1])/'SKILL.md').is_file()")
        self.assertEqual(skills.check_proposal(proposal, checks)["status"], "validated")
        (self.bundle / "SKILL.md").write_text(self.text + "Concurrent edit")
        with self.assertRaises(ValueError): skills.apply(proposal)
        (self.bundle / "SKILL.md").write_text(self.text)
        skills.apply(proposal)
        self.assertIn("Correction", (self.bundle / "SKILL.md").read_text())
        self.assertTrue((Path(proposal) / "previous-live-bundle/SKILL.md").is_file())

    def test_prepared_is_not_passed_and_evidence_required(self):
        output = self.root / "trial"
        behaviour.prepare(self.bundle, "tiny", output)
        self.assertFalse((output / "result.json").exists())
        assessment = self.root / "assessment.json"
        assessment.write_text(json.dumps({"assessor": "independent", "execution": "agent-run", "assertions": {}}))
        with self.assertRaises(ValueError): behaviour.assess(output, assessment)
        assessment.write_text(json.dumps({"assessor": "independent", "execution": "agent-run", "assertions": {
            "done": {"passed": False, "observation": "Did not finish", "evidence": [str(output / "prompt.md")]}}}))
        self.assertFalse(behaviour.assess(output, assessment)["passed"])

    def test_project_gate_requires_sources_and_cases(self):
        skills.validate(self.bundle, project=True)
        (self.bundle / "sources.md").unlink()
        with self.assertRaisesRegex(ValueError, "sources.md"):
            skills.validate(self.bundle, project=True)
        write_sources(self.bundle)
        (self.bundle / "evals/evals.json").write_text('{"schema_version":1,"skill_name":"test-skill","evals":[]}')
        with self.assertRaisesRegex(ValueError, "eval manifest"):
            skills.validate(self.bundle, project=True)


if __name__ == "__main__":
    unittest.main()
