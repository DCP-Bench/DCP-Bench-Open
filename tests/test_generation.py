"""Unit tests for durable generation bookkeeping (the evaluator is mocked)."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from generation import instances, manage, next_work


class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "skills" / "demo" / "references").mkdir(parents=True)
        (self.root / "skills" / "demo" / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
        (self.root / "skills" / "demo" / "references" / "api.md").write_text("API v1\n", encoding="utf-8")
        (self.root / "model.py").write_text("model", encoding="utf-8")
        self.patch = patch.multiple(manage, REPO_ROOT=self.root,
                                    RUNS_ROOT=self.root / "generation" / "runs",
                                    GENERATED_ROOT=self.root / "generated_models")
        self.patch.start()
        readiness = patch.object(manage, "_readiness", return_value={"image_id": "sha256:test"})
        readiness.start(); self.addCleanup(readiness.stop)

    def tearDown(self):
        self.patch.stop(); self.temp.cleanup()

    def new_attempt(self):
        manage.init("run1")
        return manage.attempt("run1", "problem", "solver", str(self.root / "skills" / "demo"))

    @staticmethod
    def accepted(path, problem="problem", solver="solver"):
        return {"accepted": True, "reason": "accepted", "problem_id": problem, "solver_id": solver,
                "requested": {"instance_count": 1, "instance_ids": None, "solution_limit": 1,
                              "tolerate_inconclusive": False},
                "limits": {key: value for key, value in manage.PROFILE_DEFAULTS.items()
                           if key not in ("instance_count", "solution_limit", "tolerate_inconclusive")},
                "model_hash": manage._sha256(path), "image": {"id": "sha256:test"},
                "instances_available": 1, "instances_checked": 1,
                "solutions_checked": 1, "unperformed_instances": [], "skipped_instances": [],
                "instances": [{"accepted": True, "solutions_checked": 1}]}

    def test_attempt_records_the_skill_by_reference_not_by_copy(self):
        """Git versions the skill, so an attempt cites it instead of copying it."""
        attempt = self.new_attempt()
        record = manage._read(attempt / "attempt.json")
        self.assertFalse((attempt / "skill").exists())
        self.assertEqual(record["skill_source"], str(Path("skills") / "demo"))
        self.assertEqual(record["skill_bundle_hash"], manage._skill_hash(self.root / "skills" / "demo"))
        self.assertEqual(set(record["skill_version"]), {"path", "commit", "modified"})
        # Every file counts, so a change anywhere in the bundle moves the hash.
        (self.root / "skills" / "demo" / "references" / "api.md").write_text("changed", encoding="utf-8")
        self.assertNotEqual(record["skill_bundle_hash"], manage._skill_hash(self.root / "skills" / "demo"))

    def test_unique_attempts_and_status_resume(self):
        first = self.new_attempt()
        second = manage.attempt("run1", "problem", "solver", str(self.root / "skills" / "demo"))
        self.assertNotEqual(first, second)
        self.assertEqual(len(manage.status("run1")["outcomes"]), 2)

    def test_setup_attempt_records_the_skill_and_numbers_attempts(self):
        manage.init("run1")
        first = manage.setup_attempt("run1", "solver", str(self.root / "skills" / "demo"))
        (self.root / "skills" / "demo" / "references" / "api.md").write_text("changed", encoding="utf-8")
        second = manage.setup_attempt("run1", "solver", str(self.root / "skills" / "demo"))
        self.assertEqual(first.name, "setup-001")
        self.assertEqual(second.name, "setup-002")
        # Each setup cites the skill as it stood then, so the edit between them shows.
        self.assertNotEqual(manage._read(first / "setup.json")["skill_bundle_hash"],
                            manage._read(second / "setup.json")["skill_bundle_hash"])
        self.assertEqual(manage._read(first / "setup.json")["agent"], "unknown")

    def test_failed_evaluation_never_retains(self):
        attempt = self.new_attempt()
        with patch("generation.manage.evaluate_model", return_value={"accepted": False, "reason": "invalid_solution"}):
            manage.evaluate(str(attempt), str(self.root / "model.py"))
        with self.assertRaises(manage.ManagementError):
            manage.retain(str(attempt))

    def test_malformed_evaluation_never_retains(self):
        attempt = self.new_attempt()
        with patch("generation.manage.evaluate_model", return_value={"accepted": True}):
            manage.evaluate(str(attempt), str(self.root / "model.py"))
        with self.assertRaises(manage.ManagementError):
            manage.retain(str(attempt))

    def test_retain_checks_candidate_bytes_and_profile(self):
        attempt = self.new_attempt()
        candidate = attempt / "candidate.py"
        with patch("generation.manage.evaluate_model", side_effect=lambda p, *_args, **_kwargs: self.accepted(p)):
            manage.evaluate(str(attempt), str(self.root / "model.py"))
        candidate.write_text("edited", encoding="utf-8")
        with self.assertRaises(manage.ManagementError):
            manage.retain(str(attempt))

    def test_retain_rejects_evaluation_with_wrong_identity_or_profile(self):
        attempt = self.new_attempt()
        with patch("generation.manage.evaluate_model", side_effect=lambda p, *_args, **_kwargs: self.accepted(p)):
            manage.evaluate(str(attempt), str(self.root / "model.py"))
        evaluation_path = attempt / "evaluation.json"
        evaluation = manage._read(evaluation_path)
        evaluation["limits"]["memory_mb"] = 2
        evaluation_path.write_text(manage._json(evaluation), encoding="utf-8")
        with self.assertRaises(manage.ManagementError):
            manage.retain(str(attempt))

    def test_unexpected_evaluator_failure_is_recorded_and_not_retained(self):
        attempt = self.new_attempt()
        with patch("generation.manage.evaluate_model", side_effect=RuntimeError("Docker disappeared")):
            result = manage.evaluate(str(attempt), str(self.root / "model.py"))
        self.assertEqual(result["reason"], "coordinator_failure")
        self.assertTrue((attempt / "coordinator_failures" / "001.json").is_file())
        self.assertFalse((attempt / "evaluation.json").exists())
        with self.assertRaises(manage.ManagementError):
            manage.retain(str(attempt))

    def test_retention_preserves_legacy_directories(self):
        attempt = self.new_attempt()
        legacy = self.root / "generated_models" / "problem" / "solver" / "model.py"
        legacy.parent.mkdir(parents=True); legacy.write_text("legacy", encoding="utf-8")
        with patch("generation.manage.evaluate_model", side_effect=lambda p, *_args, **_kwargs: self.accepted(p)):
            manage.evaluate(str(attempt), str(self.root / "model.py"))
        target = manage.retain(str(attempt))
        self.assertTrue((target / "model.py").is_file())
        self.assertEqual(legacy.read_text(encoding="utf-8"), "legacy")

    def test_traversal_and_invalid_event_are_rejected(self):
        manage.init("run1")
        with self.assertRaises(manage.ManagementError):
            manage.attempt("run1", "../x", "solver", str(self.root / "skills" / "demo"))
        with self.assertRaises(manage.ManagementError):
            manage.event("run1", "blocked", "[]")
        with self.assertRaises(manage.ManagementError):
            manage.event("run1", "attempt_evaluated", "{}")

    def test_editing_the_skill_or_the_candidate_blocks_the_attempt(self):
        """The skill an attempt cites, and the bytes it evaluated, are both fixed."""
        attempt = self.new_attempt()
        (self.root / "skills" / "demo" / "SKILL.md").write_text("edited", encoding="utf-8")
        with self.assertRaisesRegex(manage.ManagementError, "Skill bundle changed"):
            manage.evaluate(str(attempt), str(self.root / "model.py"))
        (self.root / "skills" / "demo" / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
        attempt = manage.attempt("run1", "problem", "solver", str(self.root / "skills" / "demo"))
        with patch("generation.manage.evaluate_model", side_effect=lambda p, *_args, **_kwargs: self.accepted(p)):
            manage.evaluate(str(attempt), str(self.root / "model.py"))
        (attempt / "candidate.py").write_text("swapped after evaluation", encoding="utf-8")
        with self.assertRaises(manage.ManagementError):
            manage.retain(str(attempt))

    def test_profile_supports_instance_ids_and_rejects_count_conflict(self):
        config = self.root / "config.json"
        config.write_text('{"profile":{"instance_ids":["example","json:1"]}}', encoding="utf-8")
        manage.init("run1", str(config))
        self.assertNotIn("instance_count", manage.status("run1")["run"]["profile"])
        config.write_text('{"profile":{"instance_ids":["example"],"instance_count":2}}', encoding="utf-8")
        with self.assertRaises(manage.ManagementError):
            manage.init("run2", str(config))

    def test_less_than_solution_limit_requires_exhaustion(self):
        config = self.root / "config.json"
        config.write_text('{"profile":{"solution_limit":2}}', encoding="utf-8")
        manage.init("run1", str(config))
        attempt = manage.attempt("run1", "problem", "solver", str(self.root / "skills" / "demo"))
        def exhausted(path, *_args, **_kwargs):
            result = self.accepted(path)
            result["requested"]["solution_limit"] = 2
            result["limits"] = {key: value for key, value in manage.PROFILE_DEFAULTS.items()
                                if key not in ("instance_count", "solution_limit", "tolerate_inconclusive")}
            return result
        with patch("generation.manage.evaluate_model", side_effect=exhausted):
            manage.evaluate(str(attempt), str(self.root / "model.py"))
        with self.assertRaises(manage.ManagementError):
            manage.retain(str(attempt))

    def test_exhausted_solution_coverage_uses_real_runner_status_shape(self):
        config = self.root / "config.json"
        config.write_text('{"profile":{"solution_limit":2}}', encoding="utf-8")
        manage.init("run1", str(config))
        attempt = manage.attempt("run1", "problem", "solver", str(self.root / "skills" / "demo"))
        def exhausted(path, *_args, **_kwargs):
            result = self.accepted(path)
            result["requested"]["solution_limit"] = 2
            result["instances"][0]["runner_status"] = {"type": "status", "status": "complete"}
            return result
        with patch("generation.manage.evaluate_model", side_effect=exhausted):
            manage.evaluate(str(attempt), str(self.root / "model.py"))
        target = manage.retain(str(attempt))
        self.assertTrue((target / "record.json").is_file())

    def test_instance_budget_above_supply_is_full_coverage(self):
        """A problem with one distinct instance fully covers a request for three."""
        config = self.root / "config.json"
        config.write_text('{"profile":{"instance_count":3}}', encoding="utf-8")
        manage.init("run1", str(config))
        attempt = manage.attempt("run1", "problem", "solver", str(self.root / "skills" / "demo"))
        def clamped(path, *_args, **_kwargs):
            result = self.accepted(path)
            result["requested"]["instance_count"] = 3
            return result
        with patch("generation.manage.evaluate_model", side_effect=clamped):
            manage.evaluate(str(attempt), str(self.root / "model.py"))
        self.assertTrue((manage.retain(str(attempt)) / "record.json").is_file())

    def test_unreported_instance_supply_is_refused(self):
        attempt = self.new_attempt()
        def unreported(path, *_args, **_kwargs):
            result = self.accepted(path)
            del result["instances_available"]
            return result
        with patch("generation.manage.evaluate_model", side_effect=unreported):
            manage.evaluate(str(attempt), str(self.root / "model.py"))
        with self.assertRaises(manage.ManagementError):
            manage.retain(str(attempt))

    def test_work_queue_reports_blockers_and_remaining_pairs(self):
        """An integration without readiness is unusable, so its pairs are not offered."""
        (self.root / "dataset" / "p1").mkdir(parents=True)
        (self.root / "dataset" / "p1" / "p1.cpmpy.py").write_text("x", encoding="utf-8")
        (self.root / "dataset" / "p2").mkdir(parents=True)
        (self.root / "dataset" / "p2" / "p2.cpmpy.py").write_text("x", encoding="utf-8")
        (self.root / "solvers" / "s1").mkdir(parents=True)
        (self.root / "solvers" / "s1" / "metadata.yaml").write_text("{}", encoding="utf-8")
        generated = self.root / "generated_models"
        with patch.multiple(next_work, ROOT=self.root, GENERATED=generated),              patch.object(next_work, "integration", return_value={"id": "s1", "enumeration": True}):
            unready = next_work.report()
            self.assertEqual((unready["problems"], unready["usable_integrations"]), (2, []))
            self.assertEqual(unready["eligible_pairs"], 0)
            self.assertIn("readiness", unready["integrations"][0]["blocker"])
            # Listing an unusable integration is opt-in, and still not coverage.
            self.assertEqual(next_work.report(include_unready=True)["eligible_pairs"], 2)
            # A problem with several instances comes first: hardcoding cannot hide there.
            (self.root / "dataset" / "p2" / "p2.json").write_text('[{}, {}, {}]', encoding="utf-8")
            ordered = next_work.report(include_unready=True)["next_pairs"]
            self.assertEqual([x["problem"] for x in ordered], ["p2", "p1"])
            (self.root / "dataset" / "p2" / "p2.json").unlink()
            (self.root / "solvers" / "s1" / "readiness.json").write_text("{}", encoding="utf-8")
            kept = generated / "p1" / "s1" / "run-attempt-001"
            kept.mkdir(parents=True)
            (kept / "record.json").write_text(
                '{"verdict_source": "container_evaluator", "evaluation": {"accepted": true}}', encoding="utf-8")
            with patch.object(next_work, "verify", return_value={}):
                ready = next_work.report()
        self.assertEqual(ready["usable_integrations"], ["s1"])
        self.assertEqual(ready["accepted_pairs"], 1)
        self.assertEqual(ready["next_pairs"], [{"problem": "p2", "solver": "s1", "instances": 1}])
        self.assertEqual(ready["single_instance_problems"], 2)

    def test_instance_shapes_that_no_rectangular_binder_can_take(self):
        """A ragged or mixed-type field is why a pair is impossible, not a bad model."""
        from generation.brief import describe, unbindable
        self.assertFalse(describe([[1, 2], [3, 4]])["ragged"])
        self.assertTrue(describe([[1, 2], [3]])["ragged"])
        self.assertTrue(describe([["title", 4, 13]])["mixed"])
        self.assertEqual(describe([[1, 2], [3, 4]])["shape"], "[2][2]int")
        # The two real cases this came from.
        self.assertEqual(unbindable("covering_opl"), ["Qualified"])
        self.assertEqual(unbindable("session2_movie_scheduling"), ["movies"])
        self.assertEqual(unbindable("csplib_054_n_queens"), [])

    def test_recorded_blockers_leave_the_queue(self):
        """A pair known not to be worth retrying must not keep being offered."""
        (self.root / "dataset" / "p1").mkdir(parents=True)
        (self.root / "dataset" / "p1" / "p1.cpmpy.py").write_text("x", encoding="utf-8")
        (self.root / "dataset" / "p2").mkdir(parents=True)
        (self.root / "dataset" / "p2" / "p2.cpmpy.py").write_text("x", encoding="utf-8")
        (self.root / "solvers" / "s1").mkdir(parents=True)
        (self.root / "solvers" / "s1" / "metadata.yaml").write_text("{}", encoding="utf-8")
        blockers = self.root / "blockers.json"
        with patch.multiple(next_work, ROOT=self.root, GENERATED=self.root / "generated_models",
                            BLOCKERS=blockers),              patch.object(next_work, "integration", return_value={"id": "s1", "enumeration": True}):
            self.assertEqual(next_work.report(include_unready=True)["eligible_pairs"], 2)
            # A named solver blocks only that pair.
            blockers.write_text(manage._json({"schema": 1, "blockers": [
                {"problem": "p1", "solver": "s1", "reason": "execution_timeout"}]}), encoding="utf-8")
            narrow = next_work.report(include_unready=True)
            self.assertEqual([x["problem"] for x in narrow["next_pairs"]], ["p2"])
            self.assertEqual(narrow["blocked_pairs"], ["p1 / s1"])
            # A null solver blocks the problem for every integration.
            blockers.write_text(manage._json({"schema": 1, "blockers": [
                {"problem": "p1", "solver": None, "reason": "reference_timeout"}]}), encoding="utf-8")
            self.assertEqual(next_work.report(include_unready=True)["blocked_pairs"],
                             ["p1 / every integration"])
            # A malformed or missing file must not take the queue down with it.
            blockers.write_text("not json", encoding="utf-8")
            self.assertEqual(next_work.report(include_unready=True)["eligible_pairs"], 2)

    def test_flagged_models_no_longer_cover_their_pair(self):
        """A model a later instance disproved is shown, but its pair is offered again."""
        (self.root / "dataset" / "p1").mkdir(parents=True)
        (self.root / "dataset" / "p1" / "p1.cpmpy.py").write_text("x", encoding="utf-8")
        (self.root / "solvers" / "s1").mkdir(parents=True)
        (self.root / "solvers" / "s1" / "metadata.yaml").write_text("{}", encoding="utf-8")
        kept = self.root / "generated_models" / "p1" / "s1" / "run-attempt-001"
        kept.mkdir(parents=True)
        (kept / "record.json").write_text(
            '{"verdict_source": "container_evaluator", "evaluation": {"accepted": true}}', encoding="utf-8")
        flags = self.root / "flags.json"
        with patch.multiple(next_work, ROOT=self.root, GENERATED=self.root / "generated_models", FLAGS=flags), \
             patch.object(next_work, "integration", return_value={"id": "s1", "enumeration": True}):
            self.assertEqual(next_work.report(include_unready=True)["eligible_pairs"], 0)
            flags.write_text(manage._json({"schema": 1, "flags": [
                {"model": "generated_models/p1/s1/run-attempt-001", "instance": "json:1"}]}), encoding="utf-8")
            flagged = next_work.report(include_unready=True)
            self.assertEqual(flagged["eligible_pairs"], 1)
            self.assertEqual(flagged["flagged_models"], ["generated_models/p1/s1/run-attempt-001"])
            flags.write_text("not json", encoding="utf-8")
            self.assertEqual(next_work.report(include_unready=True)["eligible_pairs"], 0)

    def test_instance_gate_refuses_what_the_example_would_not_accept(self):
        example = {"n": 3, "grid": [[1, 2], [3, 4]], "names": ["a", "b"]}
        good = {"n": 5, "grid": [[1, 2, 3]], "names": [], "note": "larger, from a generator"}
        self.assertEqual(instances.shape_failures(example, good), [])
        cases = {
            "missing fields": {"n": 5, "grid": [[1]], "note": "x"},
            "does not read": dict(good, extra=1),
            "no note": {k: v for k, v in good.items() if k != "note"},
            "note must be": dict(good, note=" "),
            "where the example has [('int',)]": dict(good, n=5.0),
            "where the example has list": dict(good, grid=7),
            "ragged": dict(good, grid=[[1, 2], [3]]),
            "mixed": dict(good, names=["a", 2]),
        }
        for expected, record in cases.items():
            with self.subTest(expected=expected):
                self.assertTrue(any(expected in failure for failure in instances.shape_failures(example, record)),
                                instances.shape_failures(example, record))
        # A field the example already has ragged may stay ragged.
        self.assertEqual(instances.shape_failures({"rows": [[1], [2, 3]]}, {"rows": [[1, 2, 3], [4]], "note": "x"}), [])

    def test_problems_recorded_as_not_extensible_are_read_from_their_section_only(self):
        text = ("# Sources\n- `elsewhere`: not in the section\n\n## Instances not added\n\nIntro with "
                "`` - `problem`: reason `` inline.\n\n- `sudoku_16`: the description fixes 9x9\n"
                "- `puzzle`: one puzzle\n\n## Dataset decisions\n- `later`: not in it either\n")
        self.assertEqual(instances.skipped_problems(text),
                         {"sudoku_16": "the description fixes 9x9", "puzzle": "one puzzle"})
        self.assertEqual(instances.skipped_problems("no such heading"), {})
        # The repository's own file must parse, whatever it currently lists.
        self.assertIsInstance(instances.skipped_problems(), dict)

    def test_append_leaves_existing_entries_byte_for_byte(self):
        path = self.root / "p.json"
        # Hand-written spacing and CRLF line ends, as a Windows checkout has them.
        original = '[\r\n  {"n": 1}\r\n  ,\r\n  {"n": 2}\r\n]\r\n'
        path.write_bytes(original.encode("utf-8"))
        ids = instances.append(path, [{"n": 3, "grid": [[1, 2], [3, 4]], "note": "x"}])
        self.assertEqual(ids, ["json:2"])
        text = path.read_bytes().decode("utf-8")
        self.assertTrue(text.startswith(original[:original.rindex("}") + 1]))
        self.assertNotIn("\n", text.replace("\r\n", ""))
        self.assertEqual(json.loads(text)[2], {"n": 3, "grid": [[1, 2], [3, 4]], "note": "x"})
        self.assertIn('      [1, 2],', text)
        empty = self.root / "e.json"
        empty.write_text("[]", encoding="utf-8")
        self.assertEqual(instances.append(empty, [{"n": 1}]), ["json:0"])

    def test_recheck_flags_model_failures_and_nothing_else(self):
        """Only a rejection that is the model's fault becomes a flag, and only once."""
        generated = self.root / "generated_models"
        outcomes = {"s_ok": ("accepted", True), "s_bad": ("invalid_solution", False),
                    "s_slow": ("execution_timeout", False), "s_infra": ("infrastructure_error", False)}
        for solver in outcomes:
            kept = generated / "p1" / solver / "attempt-001"
            kept.mkdir(parents=True)
            (kept / "model.py").write_text("model", encoding="utf-8")
            (kept / "record.json").write_text(manage._json({
                "verdict_source": "container_evaluator", "solver": solver, "model_file": "model.py",
                "evaluation": {"accepted": True, "requested": {"solution_limit": 2},
                               "limits": {"execution_timeout": 60, "reference_timeout": 60,
                                          "compilation_timeout": 120, "memory_mb": 2048, "cpus": 1}}}),
                encoding="utf-8")

        def fake(model, problem, solver, **kwargs):
            reason, accepted = outcomes[solver]
            self.assertEqual((kwargs["instance_ids"], kwargs["solution_limit"], kwargs["tolerate_inconclusive"]),
                             (["json:1"], 2, False))
            item = {"id": "json:1", "instance_hash": "h1", "accepted": accepted, "reason": reason}
            return {"accepted": accepted, "reason": reason, "detail": "d", "instances": [item],
                    "skipped_instances": [], "limits": {}, "image": {"id": "sha256:x"}}

        flags = self.root / "flags.json"
        with patch.multiple(instances, ROOT=self.root, GENERATED=generated, FLAGS=flags, evaluate=fake):
            report = instances.recheck("p1", ["json:1"], jobs=2)
            self.assertEqual((report["models"], report["passed"], report["failed"], report["inconclusive"]),
                             (4, 1, 1, 2))
            self.assertFalse(report["most_failed"])
            self.assertEqual(instances.record_flags(report["rows"]), 1)
            self.assertEqual(instances.record_flags(report["rows"]), 0)
        recorded = json.loads(flags.read_text(encoding="utf-8"))["flags"]
        self.assertEqual([(x["model"], x["instance"], x["reason"]) for x in recorded],
                         [("generated_models/p1/s_bad/attempt-001", "json:1", "invalid_solution")])

    def test_cli_error_is_clean(self):
        self.assertEqual(manage.main(["status", "--run", "missing"]), 2)


if __name__ == "__main__":
    unittest.main()
