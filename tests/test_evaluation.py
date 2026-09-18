from pathlib import Path
import os
from concurrent.futures import ProcessPoolExecutor
import tempfile
import unittest
from unittest.mock import patch
from evaluation.check import evaluate
from evaluation.execution import validate_records
from evaluation.reference import Reference, embedded_instance, load_reference, select_instances
from evaluation.results import canonical, EvaluationError, strict_json
from evaluation.reference import ReferenceSession
from evaluation.legacy import solver_id

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '''
# Data
n = 2
optimize = False
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y >= n if optimize else x + y == n)
if optimize:
    model.minimize(x + y)
model.solve()
solution = {"x": int(x.value()), "y": y.value()}
print(json.dumps(solution))
'''


def dataset_entries():
    """Yield (problem, source, label, instance) for every listed instance, plus the
    embedded example of problems whose instance list is empty."""
    for path in sorted((ROOT / "dataset").rglob("*.cpmpy.py")):
        source = path.read_text(encoding="utf-8-sig")
        json_path = path.parent / f"{path.parent.name}.json"
        records = strict_json(json_path.read_text(encoding="utf-8-sig")) if json_path.is_file() else []
        if isinstance(records, list) and records:
            for i, instance in enumerate(records):
                if isinstance(instance, dict):
                    yield path.parent.name, source, f"json:{i}", instance
        else:
            yield path.parent.name, source, "embedded", embedded_instance(source)


def _bounded_sat(source, instance, timeout=15):
    model, _ = load_reference(source, instance)
    model.solve(solver="ortools", time_limit=timeout, num_search_workers=1)
    return model.status().exitstatus.name


def _audit_entry(entry):
    return _bounded_sat(entry[1], entry[3])


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.ref = Reference(SOURCE, {"n": 2, "optimize": False}, 5)

    def test_valid_and_invalid(self):
        self.assertEqual(self.ref.check({"x": 0, "y": 2}), {"x": 0, "y": 2})
        for value in ({}, {"x": 0}, {"x": 0, "y": 2, "extra": 1}, {"x": True, "y": 2},
                      {"x": 0.0, "y": 2}, {"x": [], "y": 2}, {"x": None, "y": 2},
                      {"x": "0", "y": 2}, {"x": -1, "y": 3}, {"x": 0, "y": 0}):
            with self.subTest(value=value), self.assertRaises(EvaluationError):
                self.ref.check(value)

    def test_optimization_and_fresh_assignments(self):
        ref = Reference(SOURCE, {"n": 2, "optimize": True}, 5)
        self.assertEqual(ref.optimum, 2)
        ref.check({"x": 0, "y": 2})
        ref.check({"x": 2, "y": 0})
        with self.assertRaisesRegex(EvaluationError, "optimum"):
            ref.check({"x": 2, "y": 2})

    def test_boolean_shapes_and_objective_alias(self):
        source = '''
import cpmpy as cp
model = cp.Model()
x = cp.boolvar(shape=(2,2))
model += cp.sum(x) >= 1
model.minimize(cp.sum(x))
if model.solve():
    solution = {"matrix": x.value().astype(int).tolist(), "cost": int(model.objective_value())}
'''
        ref = Reference(source, {}, 5)
        self.assertEqual(ref.check({"matrix": [[0, True], [False, 0]], "cost": 1})["matrix"], [[False, True], [False, False]])
        for value in ([[1, 0]], [[2, 0], [0, 0]], [1, 0, 0, 0]):
            with self.assertRaises(EvaluationError):
                ref.check({"matrix": value, "cost": 1})

    def test_unsat_optimization(self):
        source = SOURCE.replace("model.solve()", "model += x < 0\nmodel.solve()")
        with self.assertRaises(EvaluationError) as caught:
            Reference(source, {"n": 2, "optimize": True}, 5)
        self.assertEqual(caught.exception.reason, "unsupported_unsat")

    def test_unsat_satisfaction(self):
        source = SOURCE.replace("model.solve()", "model += x < 0\nmodel.solve()")
        with self.assertRaises(EvaluationError) as caught:
            Reference(source, {"n": 2, "optimize": False}, 5)
        self.assertEqual(caught.exception.reason, "unsupported_unsat")

    def test_maximization(self):
        source = SOURCE.replace("model.minimize(x + y)", "model.maximize(x + y)")
        ref = Reference(source, {"n": 2, "optimize": True}, 5)
        self.assertEqual(ref.optimum, 4)
        ref.check({"x": 2, "y": 2})
        with self.assertRaises(EvaluationError): ref.check({"x": 0, "y": 2})

    def test_reference_timeout(self):
        source = SOURCE.replace("import cpmpy as cp", "import time\ntime.sleep(10)\nimport cpmpy as cp")
        with self.assertRaises(EvaluationError) as caught:
            ReferenceSession(source, {"n": 2, "optimize": False}, 0.2)
        self.assertEqual(caught.exception.reason, "reference_timeout")

    def test_real_abbots_and_golomb(self):
        path = ROOT / "dataset/abbots_puzzle/abbots_puzzle.cpmpy.py"
        ref = Reference(path.read_text(), {}, 5)
        ref.check({"men": 5, "women": 25, "children": 70})
        with self.assertRaises(EvaluationError): ref.check({"men": 5})
        path = ROOT / "dataset/csplib_006_golomb_rulers/csplib_006_golomb_rulers.cpmpy.py"
        ref = Reference(path.read_text(), {"size": 4}, 5)
        ref.check({"marks": [0, 1, 4, 6], "length": 6})
        with self.assertRaises(EvaluationError) as caught:
            ref.check({"marks": [0, 1, 4, 9], "length": 9})
        self.assertEqual(caught.exception.reason, "suboptimal_solution")

    def test_no_solve_or_print_executed(self):
        source = SOURCE.replace("model.solve()", "model.solve(unsupported_keyword=True)").replace("print(json.dumps(solution))", "raise RuntimeError('tail executed')")
        load_reference(source, {"n": 3, "optimize": False})
        with self.assertRaisesRegex(EvaluationError, "Cannot load embedded data"):
            embedded_instance(SOURCE.replace("n = 2", "n = missing_parameter"))

    def test_instances(self):
        instance, other = {"n": 2, "optimize": False}, {"n": 3, "optimize": False}
        self.assertEqual(select_instances(SOURCE, [instance, other], 2), [("example", instance), ("json:1", other)])
        self.assertEqual(select_instances(SOURCE, [], 1), [("example", instance)])
        # A count is a budget: more than exists checks everything that exists.
        self.assertEqual(select_instances(SOURCE, [instance, other], 9),
                         [("example", instance), ("json:1", other)])
        for count, ids in [(0, None), (1, ["json:0"]), (1, ["example", "example"])]:
            with self.assertRaises(EvaluationError):
                select_instances(SOURCE, [instance, other], count, ids)

    def test_instance_metadata_does_not_inflate_coverage(self):
        example = {"n": 2, "optimize": False}
        other = {"n": 3, "optimize": False, "name": "first"}
        records = [dict(example, name="example copy"), other,
                   dict(other, name="renamed", note="same inputs")]
        self.assertEqual(select_instances(SOURCE, records, 2),
                         [("example", example), ("json:1", other)])
        self.assertEqual(len(select_instances(SOURCE, records, 3)), 2)
        for kwargs in ({"ids": ["json:0"]}, {"ids": ["json:2"]}):
            with self.assertRaises(EvaluationError):
                select_instances(SOURCE, records, **kwargs)
        with self.assertRaisesRegex(EvaluationError, "missing fields"):
            select_instances(SOURCE, [{"name": "missing inputs"}])
        folder = ROOT / "dataset/csplib_002_template_design"
        source = (folder / "csplib_002_template_design.cpmpy.py").read_text()
        records = strict_json((folder / "csplib_002_template_design.json").read_text())
        selected = select_instances(source, records, 2)
        fields = embedded_instance(source)
        self.assertNotEqual(*[canonical({k: value[k] for k in fields})
                              for _, value in selected])

    def test_quasigroup_necessary_order_condition(self):
        path = ROOT / "dataset/csplib_003_quasigroup_existence/csplib_003_quasigroup_existence.json"
        for instance in strict_json(path.read_text()):
            with self.subTest(order=instance["m"]):
                self.assertIn(instance["m"] % 4, (0, 1))
                self.assertNotEqual(instance["m"], 5)

    def test_json_protocol(self):
        for value in ('{"x": 1, "x": 2}', '{"x": NaN}', '{'):
            with self.assertRaises(ValueError): strict_json(value)
        for records in ([], [{}], [{"type": "status", "status": "success"}],
                        [{"type": "status", "status": "limit"}, {"type": "solution", "values": {}}]):
            with self.assertRaises(EvaluationError): validate_records(records)

    def test_dataset_audit(self):
        unsupported = {}
        standard = {}
        files = list((ROOT / "dataset").rglob("*.cpmpy.py"))
        self.assertTrue(files)
        for path in files:
            source = path.read_text(encoding="utf-8-sig")
            try:
                expected = embedded_instance(source)
                load_reference(source, expected)
            except EvaluationError as e:
                unsupported[path.parent.name] = e.reason
                continue
            json_path = path.parent / f"{path.parent.name}.json"
            if not json_path.is_file():
                standard[path.parent.name] = "missing paired instance JSON"
                continue
            try:
                records = strict_json(json_path.read_text(encoding="utf-8-sig"))
            except ValueError as e:
                standard[path.parent.name] = f"unreadable instance file: {e}"
                continue
            if not isinstance(records, list) or any(not isinstance(x, dict) for x in records):
                standard[path.parent.name] = "instance file must be a list of objects"
                continue
            if not records:
                if expected:
                    standard[path.parent.name] = "empty instance list but nonempty data section"
                continue
            # Corpus convention: the first entry is exactly the embedded example instance.
            if canonical(records[0]) != canonical(expected):
                standard[path.parent.name] = "first instance must be exactly the embedded example"
                continue
            problems = []
            for i, instance in enumerate(records):
                if set(expected) - set(instance):
                    problems.append(f"instance {i} missing data fields")
                    continue
                try:
                    load_reference(source, instance)
                except Exception as e:
                    problems.append(f"instance {i} does not build: {type(e).__name__}: {e}")
            extra = sorted({k for x in records for k in x if k not in set(expected) | {"name", "note"}})
            if extra:
                problems.append(f"unexpected additional keys: {extra}")
            if problems:
                standard[path.parent.name] = "; ".join(problems)
        self.assertFalse(unsupported, unsupported)
        self.assertFalse(standard, standard)

    def test_fixed_references(self):
        """The two previously unsupported references load, solve, and check."""
        cases = {"csplib_012_nonogram": "board", "curious_set_of_integers": "number"}
        for problem, key in cases.items():
            with self.subTest(problem=problem):
                path = ROOT / "dataset" / problem / f"{problem}.cpmpy.py"
                source = path.read_text(encoding="utf-8-sig")
                instance = embedded_instance(source)
                ref = Reference(source, instance, 30)
                model, outputs = load_reference(source, instance)
                self.assertTrue(model.solve(solver="ortools", num_search_workers=1))
                values = {}
                for name, expr in outputs.items():
                    value = expr.value()
                    values[name] = value.tolist() if hasattr(value, "tolist") else int(value)
                self.assertEqual(ref.check(values), values)
                if key == "board":
                    wrong = {"board": [list(row) for row in values["board"]]}
                    wrong["board"][0][0] = 1 - wrong["board"][0][0]
                else:
                    wrong = {key: values[key] + 1}
                with self.assertRaises(EvaluationError):
                    ref.check(wrong)

    def test_multiple_nonogram_instances(self):
        """Name-bearing csplib instances pass through the reference loader."""
        folder = ROOT / "dataset" / "csplib_012_nonogram"
        source = (folder / "csplib_012_nonogram.cpmpy.py").read_text(encoding="utf-8-sig")
        records = strict_json((folder / "csplib_012_nonogram.json").read_text(encoding="utf-8-sig"))
        named = [x for x in records if "name" in x]
        self.assertTrue(named)
        for instance in (named[0], named[4]):  # soccer_player, castle
            with self.subTest(instance=instance.get("name")):
                model, outputs = load_reference(source, instance)
                self.assertTrue(model.solve(solver="ortools", time_limit=30, num_search_workers=1))
                values = {name: expr.value().tolist() for name, expr in outputs.items()}
                ref = Reference(source, instance, 60)
                self.assertEqual(ref.check(values), values)


    @unittest.skipUnless(os.environ.get("DCP_UNSAT_AUDIT") == "1",
                         "Set DCP_UNSAT_AUDIT=1 for the bounded satisfiability audit")
    def test_no_unsat_instances(self):
        """No listed instance (or embedded example) may be provably UNSAT.

        Bounded 15-second OR-Tools search per instance; an instance left
        UNKNOWN is not a failure, only a provably UNSAT one is.
        """
        entries = list(dataset_entries())
        with ProcessPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
            statuses = list(pool.map(_audit_entry, entries))
        unsat = [f"{entry[0]} {entry[2]}" for entry, status in zip(entries, statuses)
                 if status == "UNSATISFIABLE"]
        self.assertFalse(unsat, f"Provably UNSAT instances: {unsat}")


class OrchestrationTests(unittest.TestCase):
    def run_records(self, records, **kwargs):
        with tempfile.TemporaryDirectory() as temp:
            model = Path(temp) / "model.py"
            model.write_text("# deliberately not executable on host")
            with patch("evaluation.check.image_identity", return_value="sha256:test"), patch("evaluation.check.execute", return_value=(records, {})):
                return evaluate(model, "tiny", "cpmpy_python", reference_source=SOURCE, instances=[], **kwargs)

    def test_solution_count_is_bounded(self):
        """Duplicate records must not each cost a reference solve."""
        one = {"type": "solution", "values": {"x": 0, "y": 2}}
        status = {"type": "status", "status": "complete"}
        checks = []
        real = ReferenceSession.check
        with patch.object(ReferenceSession, "check", lambda s, v: checks.append(v) or real(s, v)):
            result = self.run_records([one] * 50 + [status], solution_limit=2)
        self.assertEqual(result["reason"], "invalid_output")
        self.assertEqual(checks, [])
        checks.clear()
        with patch.object(ReferenceSession, "check", lambda s, v: checks.append(v) or real(s, v)):
            self.assertTrue(self.run_records([one, one, status], solution_limit=2)["accepted"])
        self.assertEqual(len(checks), 2)

    def test_exhaustion_and_duplicates(self):
        one = {"type": "solution", "values": {"x": 0, "y": 2}}
        for status, accepted, reason in (("limit", False, "invalid_output"), ("complete", True, "accepted"),
                                         ("timeout", False, "execution_timeout")):
            result = self.run_records([one, one, {"type": "status", "status": status}], solution_limit=2)
            self.assertEqual((result["accepted"], result["reason"]), (accepted, reason), result)
        self.assertFalse(self.run_records([{"type": "status", "status": "complete"}])["accepted"])

    def test_tolerating_inconclusive_instances(self):
        """Skipping a timeout relaxes coverage; it must never relax soundness."""
        good = {"type": "solution", "values": {"x": 0, "y": 2}}
        bad = {"type": "solution", "values": {"x": 0, "y": 0}}
        stop = {"type": "status", "status": "limit"}
        with tempfile.TemporaryDirectory() as temp:
            model = Path(temp) / "model.py"
            model.write_text("# stub")
            second = [{"n": 3, "optimize": False}]

            def run(records, **kwargs):
                with patch("evaluation.check.image_identity", return_value="sha256:test"),                      patch("evaluation.check.execute", side_effect=records):
                    return evaluate(model, "tiny", "cpmpy_python", reference_source=SOURCE,
                                    instances=second, instance_count=2, **kwargs)

            # The first instance times out in the container, the second is fine.
            timeout = [{"type": "status", "status": "timeout"}]
            records = [(timeout, {}), ([{"type": "solution", "values": {"x": 0, "y": 3}}, stop], {})]
            strict = run(list(records))
            self.assertEqual((strict["accepted"], strict["reason"]), (False, "execution_timeout"))
            self.assertEqual(strict["skipped_instances"], [])

            lenient = run(list(records), tolerate_inconclusive=True)
            self.assertTrue(lenient["accepted"], lenient)
            self.assertEqual(lenient["skipped_instances"], ["example"])
            self.assertEqual(lenient["instances_checked"], 1)
            self.assertTrue(lenient["instances"][0]["skipped"])
            self.assertEqual(lenient["requested"]["tolerate_inconclusive"], True)

            # A rejected solution still fails, tolerated or not.
            counterexample = [([bad, stop], {}), ([good, stop], {})]
            for tolerate in (False, True):
                with self.subTest(tolerate=tolerate):
                    result = run(list(counterexample), tolerate_inconclusive=tolerate)
                    self.assertEqual(result["reason"], "invalid_solution", result)

            # Nothing verified at all cannot pass.
            nothing = [(timeout, {}), (timeout, {})]
            empty = run(list(nothing), tolerate_inconclusive=True)
            self.assertEqual((empty["accepted"], empty["reason"]), (False, "no_instance_verified"))
            self.assertEqual(len(empty["skipped_instances"]), 2)

    def test_reference_and_instance_errors(self):
        self.assertEqual(self.run_records([], instance_count=0)["reason"], "invalid_request")
        self.assertEqual(self.run_records([], instance_ids=["json:0"])["reason"], "invalid_request")
        self.assertEqual(self.run_records([], execution_timeout=-1)["reason"], "invalid_request")

    def test_instance_budget_is_not_a_requirement(self):
        """Asking for more instances than exist checks every one that exists."""
        records = [{"type": "solution", "values": {"x": 0, "y": 2}}, {"type": "status", "status": "limit"}]
        result = self.run_records(records, instance_count=7)
        self.assertTrue(result["accepted"], result)
        self.assertEqual((result["instances_available"], result["instances_checked"]), (1, 1))
        self.assertEqual(result["requested"]["instance_count"], 7)

    def test_counterexample_survives_a_bad_ending(self):
        """A rejected solution disproves the model however the run ended."""
        good = {"type": "solution", "values": {"x": 0, "y": 2}}
        bad = {"type": "solution", "values": {"x": 0, "y": 0}}
        for ending in ("timeout", "error", "limit", "complete"):
            with self.subTest(ending=ending):
                result = self.run_records([good, bad, {"type": "status", "status": ending}], solution_limit=5)
                self.assertEqual(result["reason"], "invalid_solution", result)
                self.assertEqual(result["instances"][0]["solutions_checked"], 1)

    def test_clean_solutions_then_a_bad_ending_are_inconclusive(self):
        good = {"type": "solution", "values": {"x": 0, "y": 2}}
        for ending, reason in (("timeout", "execution_timeout"), ("error", "execution_error")):
            with self.subTest(ending=ending):
                result = self.run_records([good, {"type": "status", "status": ending}], solution_limit=5)
                self.assertEqual(result["reason"], reason, result)
                # The verified work is still reported, so a consumer can weigh it.
                self.assertEqual(result["instances"][0]["solutions_checked"], 1)

    def test_legacy_framework_names_map_onto_integrations(self):
        """eval.py takes a framework name from a third party's JSONL. A known
        name maps onto an integration; an unknown one is passed through to fail
        as a missing integration, never run as arbitrary host Python."""
        self.assertEqual(solver_id("CPMpy"), "cpmpy_python")
        self.assertEqual(solver_id("or-tools"), "ortools_cp_sat_python")
        self.assertEqual(solver_id("z3"), "z3")

    def test_stop_at_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            model = Path(temp) / "model.py"
            model.write_text("# stub")
            records = [{"type": "solution", "values": {}}, {"type": "status", "status": "limit"}]
            with patch("evaluation.check.image_identity", return_value="sha256:test"), patch("evaluation.check.execute", return_value=(records, {})) as execute:
                result = evaluate(model, "tiny", "cpmpy_python", reference_source=SOURCE,
                                  instances=[{"n": 3, "optimize": False}], instance_count=2)
                self.assertFalse(result["accepted"])
                self.assertEqual(result["unperformed_instances"], ["json:0"])
                self.assertEqual(execute.call_count, 1)

    def test_model_is_snapshotted(self):
        with tempfile.TemporaryDirectory() as temp:
            model = Path(temp) / "model.py"
            model.write_bytes(b"original")
            received = []
            def runner(path, instance, *args, **kwargs):
                received.append(kwargs["model_bytes"])
                model.write_bytes(b"changed during evaluation")
                return ([{"type": "solution", "values": {"x": 0, "y": instance["n"]}},
                         {"type": "status", "status": "limit"}], {})
            with patch("evaluation.check.image_identity", return_value="sha256:test"), patch("evaluation.check.execute", side_effect=runner):
                result = evaluate(model, "tiny", "cpmpy_python", reference_source=SOURCE,
                                  instances=[{"n": 3, "optimize": False}], instance_count=2)
            self.assertTrue(result["accepted"], result)
            self.assertEqual(received, [b"original", b"original"])


if __name__ == "__main__":
    unittest.main()
