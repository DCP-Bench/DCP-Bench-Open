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
          "z3_python": "model_z3.py", "clingo_asp": "model_clingo.lp",
          "swipl_clpfd": "model_swipl.pl", "pulp_cbc": "model_pulp.py",
          "pumpkin_rust": "model.rs", "choco_python": "model_choco.py",
          "pysat": "model_pysat.py", "hermax": "model_hermax.py",
          "exact": "model_exact.py"}

# Integrations whose metadata says they cannot optimize. The pilot cases that
# need an objective are not run for these, and they carry no MAXIMIZATION_SWAPS
# entry, because there is no direction in their fixture to turn around.
def satisfaction_only(solver):
    path = ROOT / "solvers" / solver / "metadata.yaml"
    return json.loads(path.read_text(encoding="utf-8")).get("optimization", True) is False

# The minimize/maximize spelling each pilot fixture uses, so `test_maximization`
# can turn it around. Kept beside PILOTS because the two are added together.
MAXIMIZATION_SWAPS = {"cpmpy_python": ("minimize", "maximize"), "ortools_cp_sat_python": ("minimize", "maximize"),
                      "ortools_cp_sat_cpp": ("Minimize", "Maximize"), "minizinc_gecode": ("minimize", "maximize"),
                      "z3_python": ("minimize", "maximize"),
                      "clingo_asp": ("minimize", "maximize"),
                      "swipl_clpfd": ("min(", "max("),
                      "pulp_cbc": ("LpMinimize", "LpMaximize"),
                      "pumpkin_rust": ("minimise", "maximise"),
                      "choco_python": ("minimize", "maximize"),
                      "hermax": ("minimize", "maximize"),
                      "exact": ("minimise", "maximise")}

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


class MetadataTests(unittest.TestCase):
    """What every integration declares about itself, checked without Docker.

    `paradigms` is how the catalogue website groups integrations, and a tag
    outside the vocabulary would not fail anywhere: it would quietly split a
    column into two. So the vocabulary is a file, and this is what holds the
    integrations to it.
    """

    def setUp(self):
        self.vocabulary = json.loads(
            (ROOT / "solvers/paradigms.json").read_text(encoding="utf-8"))
        self.integrations = {
            path.parent.name: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((ROOT / "solvers").glob("*/metadata.yaml"))
        }
        # An integration counts as certified once it carries a readiness record,
        # which is also what next_work uses to decide it may be used at all.
        self.certified = {
            solver: metadata for solver, metadata in self.integrations.items()
            if (ROOT / "solvers" / solver / "readiness.json").is_file()
        }

    def test_paradigm_vocabulary_is_well_formed(self):
        identifiers = [entry["id"] for entry in self.vocabulary]
        self.assertTrue(identifiers)
        self.assertCountEqual(identifiers, set(identifiers), "duplicate paradigm ID")
        for entry in self.vocabulary:
            with self.subTest(paradigm=entry.get("id")):
                self.assertEqual(set(entry), {"id", "name", "summary"})
                # The website prints the name and summary verbatim.
                self.assertRegex(entry["id"], r"^[a-z][a-z0-9_]*$")
                self.assertTrue(entry["name"].strip())
                self.assertTrue(entry["summary"].strip().endswith("."))

    def test_every_integration_has_a_distinct_display_name(self):
        """The catalogue groups models by integration ID and labels them with
        `name`, so two integrations sharing a name would be two tabs a reader
        cannot tell apart."""
        names = {}
        for solver, metadata in self.integrations.items():
            with self.subTest(solver=solver):
                name = metadata.get("name")
                self.assertIsInstance(name, str)
                self.assertTrue(name.strip(), "declare a display name")
                self.assertNotIn(name, names,
                                 f"{solver} and {names.get(name)} share the name {name!r}")
                names[name] = solver

    def test_every_integration_declares_known_paradigms(self):
        known = {entry["id"] for entry in self.vocabulary}
        self.assertTrue(self.integrations, "no integrations found under solvers/")
        for solver, metadata in self.integrations.items():
            with self.subTest(solver=solver):
                paradigms = metadata.get("paradigms")
                self.assertIsInstance(paradigms, list, "declare paradigms as a list")
                self.assertTrue(paradigms, "declare at least one paradigm")
                self.assertCountEqual(paradigms, set(paradigms), "repeated paradigm")
                for tag in paradigms:
                    self.assertIn(tag, known, f"add {tag!r} to solvers/paradigms.json first")

    def test_every_language_has_a_website_row(self):
        """`language` picks the label and the grammar above every model of an
        integration. A value `generate_site.py` does not know is not an error
        there: the page just renders the model unlabelled and uncoloured, which
        nobody notices until they look at it."""
        import generate_site

        for solver, metadata in self.integrations.items():
            with self.subTest(solver=solver):
                language = metadata.get("language")
                self.assertIn(language, generate_site.LANGUAGES,
                              f"add a {language!r} row to LANGUAGES in generate_site.py")
                self.assertIn(metadata["extension"], generate_site.EXTENSION_LANGUAGE,
                              f"add {metadata['extension']!r} to EXTENSION_LANGUAGE in generate_site.py")

    def test_every_certified_integration_is_a_pilot(self):
        """The pilot suite is what proves an integration still round-trips after
        a shared runner change. An integration missing from PILOTS is not tested
        by it and nothing else says so."""
        self.assertTrue(self.certified, "no certified integrations found under solvers/")
        for solver in self.certified:
            with self.subTest(solver=solver):
                self.assertIn(solver, PILOTS, f"add {solver} to PILOTS in this file")
                fixture = ROOT / "tests/fixtures" / PILOTS[solver]
                self.assertTrue(fixture.is_file(), f"missing pilot fixture {fixture}")
                if not satisfaction_only(solver):
                    self.assertIn(solver, MAXIMIZATION_SWAPS,
                                  f"add {solver} to MAXIMIZATION_SWAPS in this file")

    def test_readme_names_every_certified_integration(self):
        """The README's list drifted once already: PyChoco was certified and
        went unlisted, because nothing checked. This checks the names, not the
        sentence around them, so the prose stays free. It catches an omission
        rather than a stale entry, which is the direction that actually drifts."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for solver, metadata in self.certified.items():
            with self.subTest(solver=solver):
                self.assertIn(metadata["name"], readme,
                              f"README.md does not name the certified integration {metadata['name']!r}")


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
        replacements = MAXIMIZATION_SWAPS
        for solver, filename in PILOTS.items():
            if satisfaction_only(solver):
                continue
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
                if optimize and satisfaction_only(solver):
                    continue
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
