"""Opt-in real evaluator tests for the bookkeeping boundary, not agent behaviour."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from generation import manage
from evaluation.execution import image_identity, integration


@unittest.skipUnless(os.environ.get("DCP_CONTAINER_TESTS") == "1", "Requires existing CPMpy pilot image")
class GenerationContainerTests(unittest.TestCase):
    def test_failed_then_repaired_model_and_exhausted_retention(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            # Tests the bookkeeping boundary with the already-tested pilot;
            # readiness validation has its own independent fixture tests.
            identity = image_identity(integration("cpmpy_python"))
            with patch.multiple(manage, REPO_ROOT=root, RUNS_ROOT=root / "generation/runs", GENERATED_ROOT=root / "generated_models"), patch.object(manage, "_readiness", return_value={"image_id": identity}):
                skill = root / "skills/test-solver"
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text("---\nname: test-solver\ndescription: Test CPMpy submissions.\n---\nUse build(instance).\n")
                config = root / "config.json"
                config.write_text(json.dumps({"agent": "deterministic test fixture", "profile": {"solution_limit": 2}}))
                manage.init("repair", str(config))
                model = root / "model.py"
                prefix = "import cpmpy as cp\ndef build(instance):\n    men, women, children = cp.intvar(0,100,shape=3)\n"
                tail = "    return model, {'men': men, 'women': women, 'children': children}\n"
                model.write_text(prefix + "    model=cp.Model(men==0,women==0,children==100)\n" + tail)
                failed = manage.attempt("repair", "abbots_puzzle", "cpmpy_python", str(skill))
                result = manage.evaluate(str(failed), str(model))
                self.assertFalse(result["accepted"], result)
                with self.assertRaises(manage.ManagementError): manage.retain(str(failed))
                prior = hashlib.sha256((failed / "candidate.py").read_bytes()).hexdigest()
                model.write_text(prefix + "    model=cp.Model(men+women+children==100,6*men+4*women+children==200,women==5*men)\n" + tail)
                repaired = manage.attempt("repair", "abbots_puzzle", "cpmpy_python", str(skill))
                result = manage.evaluate(str(repaired), str(model))
                self.assertTrue(result["accepted"], result)
                self.assertEqual(result["solutions_checked"], 1)
                self.assertEqual(result["instances"][0]["runner_status"]["status"], "complete")
                retained = manage.retain(str(repaired))
                record = json.loads((retained / "record.json").read_text(encoding="utf-8"))
                self.assertEqual(record["verdict_source"], "container_evaluator")
                self.assertEqual(record["evaluation"], json.loads((repaired / "evaluation.json").read_text(encoding="utf-8")))
                self.assertEqual(hashlib.sha256((retained / "model.py").read_bytes()).hexdigest(), result["model_hash"])
                self.assertEqual(hashlib.sha256((failed / "candidate.py").read_bytes()).hexdigest(), prior)
                with self.assertRaises(manage.ManagementError): manage.retain(str(repaired))
                state = manage.status("repair")
                self.assertEqual([x["retained"] for x in state["outcomes"]], [False, True])


if __name__ == "__main__":
    unittest.main()
