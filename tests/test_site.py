"""What the catalogue build computes, rather than how it looks. No Docker.

Two things are covered: the paradigm breakdown, including the decisions the page
rests on — a model carrying no verdict of this evaluator's is excluded, a
documented paradigm with no integration still gets a row, and an integration
declaring two paradigms counts towards both — and the link each model carries
back to its source file.
"""
import unittest
from pathlib import Path

import generate_site

VOCABULARY = [
    {"id": "cp", "name": "Constraint programming", "summary": "Domains and propagation."},
    {"id": "mip", "name": "Mixed integer programming", "summary": "Linear inequalities."},
    {"id": "sat", "name": "Boolean satisfiability", "summary": "Clauses."},
]
INTEGRATIONS = {
    "pure_cp": {"id": "pure_cp", "name": "Pure", "paradigms": ["cp"]},
    "hybrid": {"id": "hybrid", "name": "Hybrid", "paradigms": ["cp", "mip"]},
}


def verified(solver):
    return {"metrics": {"solver": solver, "verdict_source": "container_evaluator"}}


def foreign(solver):
    """A record no integration here produced — nothing to read a paradigm off."""
    return {"metrics": {"solver": solver, "verdict_source": "elsewhere"}}


# Keyed on the integration ID, as load_generated_models() keys it.
# queens has a model from each integration; magic only from the hybrid one.
GENERATED = {
    "queens": {"pure_cp": [verified("pure_cp")], "hybrid": [verified("hybrid")],
               "cpmpy": [foreign("cpmpy")]},
    "magic": {"hybrid": [verified("hybrid")]},
}


class ParadigmBreakdownTests(unittest.TestCase):
    def setUp(self):
        self.breakdown = generate_site.paradigm_breakdown(GENERATED, INTEGRATIONS, VOCABULARY)
        self.by_id = {item["id"]: item for item in self.breakdown["paradigms"]}

    def test_a_multi_paradigm_integration_counts_towards_each_of_them(self):
        self.assertEqual(self.by_id["mip"]["models"], 2)
        self.assertEqual(self.by_id["mip"]["problems"], {"queens", "magic"})
        self.assertEqual(self.by_id["cp"]["integrations"], ["hybrid", "pure_cp"])
        self.assertEqual(self.by_id["mip"]["integrations"], ["hybrid"])
        # Which is why the per-paradigm counts exceed the three verified models,
        # and why the page says so rather than inviting the reader to add them up.
        self.assertEqual(sum(item["models"] for item in self.breakdown["paradigms"]), 5)
        self.assertEqual(sum(self.breakdown["integration_models"].values()), 3)

    def test_a_model_without_this_evaluators_verdict_is_left_out(self):
        self.assertNotIn("cpmpy", self.breakdown["integration_models"])
        self.assertEqual(self.breakdown["integration_models"], {"pure_cp": 1, "hybrid": 2})
        self.assertEqual(self.breakdown["integration_problems"], {"pure_cp": 1, "hybrid": 2})

    def test_a_paradigm_without_an_integration_keeps_an_empty_row(self):
        self.assertEqual(self.by_id["sat"]["integrations"], [])
        self.assertEqual(self.by_id["sat"]["models"], 0)
        self.assertEqual(self.by_id["sat"]["problems"], set())

    def test_paradigms_are_ranked_by_how_much_of_the_catalogue_they_cover(self):
        self.assertEqual([item["id"] for item in self.breakdown["paradigms"]],
                         ["cp", "mip", "sat"])

    def test_per_problem_tags_drive_the_catalogue_filter(self):
        self.assertEqual(self.breakdown["per_problem"],
                         {"queens": ["cp", "mip"], "magic": ["cp", "mip"]})

    def test_an_undocumented_tag_is_reported_rather_than_dropped(self):
        breakdown = generate_site.paradigm_breakdown(
            {"queens": {"Odd": [verified("odd")]}},
            {"odd": {"id": "odd", "paradigms": ["nonesuch"]}},
            VOCABULARY,
        )
        rows = {item["id"]: item for item in breakdown["paradigms"]}
        self.assertEqual(rows["nonesuch"]["models"], 1)
        self.assertIn("paradigms.json", rows["nonesuch"]["summary"])


class ModelLinkTests(unittest.TestCase):
    """The "Model file (GitHub)" link, which has to name a directory that exists.

    The link is built from the integration ID (`cpmpy_python`), never from the
    display name (`CPMpy`). Deriving the first from the second is what once
    pointed 606 of these links at `cpmpy — python/`.
    """

    def test_the_link_names_the_directory_the_model_lives_in(self):
        entry = {
            "submission": "attempt-001", "directory": "cpmpy_python",
            "model_file": "model.py", "code": "",
            "metrics": {"problem": "queens", "solver": "cpmpy_python", "verdict": {}},
        }
        rendered = generate_site.generated_model_html(entry)
        self.assertIn("generated_models/queens/cpmpy_python/attempt-001/model.py", rendered)
        self.assertNotIn("CPMpy", rendered)

    def test_every_model_in_the_repository_is_linked_to_a_real_file(self):
        root = Path(generate_site.GENERATED_DIR)
        checked = 0
        for problem, by_framework in generate_site.load_generated_models().items():
            for entries in by_framework.values():
                for entry in entries:
                    if not entry["model_file"]:
                        continue
                    path = root / problem / entry["directory"] / entry["submission"] / entry["model_file"]
                    self.assertTrue(path.is_file(), path)
                    checked += 1
        self.assertGreater(checked, 500, "the corpus should not have shrunk to nothing")


class RealRepositoryTests(unittest.TestCase):
    """The vocabulary and the integration metadata, as the site build reads them."""

    def test_every_declared_paradigm_reaches_the_page(self):
        vocabulary = generate_site.load_paradigm_vocabulary()
        integrations = generate_site.load_integrations()
        self.assertTrue(vocabulary)
        self.assertTrue(integrations)
        documented = {entry["id"] for entry in vocabulary}
        for solver, metadata in integrations.items():
            with self.subTest(solver=solver):
                self.assertTrue(set(metadata.get("paradigms") or []) <= documented)


if __name__ == "__main__":
    unittest.main()
