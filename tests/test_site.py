"""The catalogue's paradigm breakdown. No Docker, no dataset.

An integration may declare more than one paradigm, and none in this repository
does yet, so the site build never meets that case on real data. This is where it
is exercised, along with the two decisions the page rests on: leaderboard
imports are excluded, and a documented paradigm with no integration still gets
a row.
"""
import unittest

import generate_site

VOCABULARY = [
    {"id": "cp", "name": "Constraint programming", "summary": "Domains and propagation."},
    {"id": "mip", "name": "Mixed integer programming", "summary": "Linear inequalities."},
    {"id": "sat", "name": "Boolean satisfiability", "summary": "Clauses."},
]
INTEGRATIONS = {
    "pure_cp": {"id": "pure_cp", "paradigms": ["cp"]},
    "hybrid": {"id": "hybrid", "paradigms": ["cp", "mip"]},
}


def verified(solver):
    return {"metrics": {"solver": solver, "verdict_source": "container_evaluator"}}


def imported(solver):
    return {"metrics": {"solver": solver, "verdict_source": "leaderboard"}}


# queens has a model from each integration; magic only from the hybrid one.
GENERATED = {
    "queens": {"Pure": [verified("pure_cp")], "Hybrid": [verified("hybrid")],
               "CPMpy": [imported("cpmpy")]},
    "magic": {"Hybrid": [verified("hybrid")]},
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

    def test_imported_leaderboard_models_are_left_out(self):
        self.assertNotIn("cpmpy", self.breakdown["integration_models"])
        self.assertEqual(self.breakdown["integration_models"], {"pure_cp": 1, "hybrid": 2})
        self.assertEqual(self.breakdown["integration_problems"], {"pure_cp": 1, "hybrid": 2})

    def test_a_paradigm_without_an_integration_keeps_an_empty_row(self):
        self.assertEqual(self.by_id["sat"]["integrations"], [])
        self.assertEqual(self.by_id["sat"]["models"], 0)
        self.assertEqual(self.by_id["sat"]["problems"], set())
        self.assertNotIn("sat", generate_site.paradigm_overlap_matrix(self.breakdown["paradigms"]))

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
