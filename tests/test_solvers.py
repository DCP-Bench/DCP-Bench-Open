import json
import os
from pathlib import Path
import tempfile
import unittest
from evaluation import evaluate
from evaluation.execution import image_identity, run_process
from evaluation.results import EvaluationError
from tests.test_evaluation import SOURCE, ROOT

PILOTS = {"cpmpy_python": "model_cpmpy.py", "ortools_cp_sat_python": "model_cp_sat.py",
          "ortools_cp_sat_cpp": "model.cpp", "minizinc_gecode": "model.mzn",
          "z3_python": "model_z3.py", "clingo_asp": "model_clingo.lp"}

# n-queens, with the board size left as a placeholder so the same model can be
# written either instance-agnostically or with the embedded example baked in.
QUEENS = '''import numpy as np
import cpmpy as cp


def build(instance):
    n = SIZE
    q = cp.intvar(1, n, shape=n, name="queens")
    return cp.Model([cp.AllDifferent(q), cp.AllDifferent(q - np.arange(n)),
                     cp.AllDifferent(q + np.arange(n))]), {"queens": q}
'''


@unittest.skipUnless(os.environ.get("DCP_CONTAINER_TESTS") == "1", "Set DCP_CONTAINER_TESTS=1 after building images")
class ContainerTests(unittest.TestCase):
    def test_unconstrained_outputs_and_float_rejection(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "model.py"
            path.write_text("import cpmpy as cp\ndef build(instance):\n    return cp.Model(), {'x': cp.intvar(0,2), 'y': 2}\n")
            source = SOURCE.replace("x + y >= n if optimize else x + y == n", "y == n")
            result = evaluate(path, "tiny", "cpmpy_python", reference_source=source, solution_limit=4)
            self.assertTrue(result["accepted"], result)
            self.assertEqual(result["solutions_checked"], 3)
            path.write_text("import cpmpy as cp\ndef build(instance):\n    return cp.Model(), {'x': 0.5, 'y': 2}\n")
            result = evaluate(path, "tiny", "cpmpy_python", reference_source=SOURCE)
            self.assertFalse(result["accepted"], result)

    def test_instance_budget_catches_a_hardcoded_model(self):
        """The campaign profile's whole purpose: one instance hides hardcoding.

        n-queens lists six instances (n=10..15). A model that bakes in the
        embedded example passes while only that instance is checked, and is
        caught on the second one.
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "model.py"
            for size, agnostic in (("10", False), ("instance['n']", True)):
                with self.subTest(hardcoded=not agnostic):
                    path.write_text(QUEENS.replace("SIZE", size))
                    one = evaluate(path, "csplib_054_n_queens", "cpmpy_python")
                    self.assertTrue(one["accepted"], one)
                    self.assertEqual(one["instances_available"], 6)
                    every = evaluate(path, "csplib_054_n_queens", "cpmpy_python", instance_count=99)
                    self.assertEqual(every["accepted"], agnostic, every)
                    self.assertEqual(every["instances_checked"], 6 if agnostic else 1)
                    if not agnostic:
                        self.assertEqual(every["reason"], "invalid_output")

    def test_minizinc_satisfaction(self):
        with tempfile.TemporaryDirectory() as temp:
            model = Path(temp) / "model.mzn"
            model.write_text((ROOT / "tests/fixtures/model.mzn").read_text().replace("solve minimize objective;", "solve satisfy;"))
            result = evaluate(model, "tiny", "minizinc_gecode", reference_source=SOURCE, solution_limit=4)
            self.assertTrue(result["accepted"], result)
            self.assertEqual(result["solutions_checked"], 3)

    def test_maximization(self):
        replacements = {"cpmpy_python": ("minimize", "maximize"), "ortools_cp_sat_python": ("minimize", "maximize"),
                        "ortools_cp_sat_cpp": ("Minimize", "Maximize"), "minizinc_gecode": ("minimize", "maximize"),
                        "z3_python": ("minimize", "maximize"),
                        "clingo_asp": ("minimize", "maximize")}
        for solver, filename in PILOTS.items():
            with self.subTest(solver=solver), tempfile.TemporaryDirectory() as temp:
                original = ROOT / "tests/fixtures" / filename
                model = Path(temp) / ("model" + original.suffix)
                model.write_text(original.read_text().replace(*replacements[solver]))
                source = SOURCE.replace("optimize = False", "optimize = True").replace("minimize", "maximize")
                result = evaluate(model, "tiny", solver, reference_source=source, solution_limit=2)
                self.assertTrue(result["accepted"], result)
                self.assertEqual(result["solutions_checked"], 1)

    def test_legacy_jsonl_cli(self):
        from click.testing import CliRunner
        from eval import main
        with CliRunner().isolated_filesystem():
            dataset = {"id": "tiny", "example_instance": "n = 2\noptimize = False",
                       "model": SOURCE.split("# End of data")[1]}
            Path("dataset.jsonl").write_text(json.dumps(dataset) + "\n")
            for code, accepted in [('print(\'{"x": 0, "y": 2}\')', True), ('print(\'{"x": 0}\')', False)]:
                Path("models.jsonl").write_text(json.dumps({"id": "tiny", "model": code}) + "\n")
                result = CliRunner().invoke(main, ["--dataset_file", "dataset.jsonl", "--test_file", "models.jsonl", "--modelling_framework", "CPMpy"])
                self.assertEqual(result.exit_code, 0 if accepted else 1, result.output)
                self.assertEqual(json.loads(Path("summary.txt").read_text())["accepted"], accepted)

    def test_pilots(self):
        for solver, filename in PILOTS.items():
            for optimize in (False, True):
                with self.subTest(solver=solver, optimize=optimize):
                    source = SOURCE.replace("optimize = False", f"optimize = {optimize}")
                    result = evaluate(ROOT / "tests/fixtures" / filename, "tiny", solver,
                                      reference_source=source, instances=[{"n": 3, "optimize": optimize}],
                                      instance_count=2, solution_limit=5)
                    self.assertTrue(result["accepted"], json.dumps(result, indent=2))
                    self.assertEqual(result["solutions_checked"], 7)

    def test_compilation_error(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "model.cpp"
            path.write_text("not C++")
            result = evaluate(path, "tiny", "ortools_cp_sat_cpp", reference_source=SOURCE)
            self.assertEqual(result["reason"], "compilation_error", result)

    def test_timeout_and_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "model.py"
            path.write_text("import time\ndef build(instance):\n    time.sleep(60)\n")
            result = evaluate(path, "tiny", "cpmpy_python", reference_source=SOURCE, execution_timeout=1)
            self.assertEqual(result["reason"], "execution_timeout", result)
        code, out, _ = run_process(["docker", "ps", "-a", "--filter", "name=dcp-eval-", "--format", "{{.Names}}"], 10)
        self.assertEqual(out.strip(), "")

    def test_isolation(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "model.py"
            path.write_text('''
import os, socket
def build(instance):
    assert os.getuid() != 0
    assert not os.path.exists('/dataset')
    assert sorted(os.listdir('/input')) == ['model.py', 'request.json']
    try:
        open('/input/changed', 'w')
        raise AssertionError('input writable')
    except OSError: pass
    try:
        open('/changed', 'w')
        raise AssertionError('root writable')
    except OSError: pass
    s = socket.socket(); s.settimeout(0.2)
    assert s.connect_ex(('1.1.1.1', 443)) != 0
    import cpmpy as cp
    x = cp.intvar(0, 2)
    return cp.Model(x == 0), {'x': x, 'y': 2}
''')
            result = evaluate(path, "tiny", "cpmpy_python", reference_source=SOURCE)
            self.assertTrue(result["accepted"], result)

    def test_missing_image(self):
        with self.assertRaises(EvaluationError) as caught:
            image_identity({"image": "dcp-eval/does-not-exist:test", "id": "missing"})
        self.assertEqual(caught.exception.reason, "infrastructure_error")


if __name__ == "__main__":
    unittest.main()
