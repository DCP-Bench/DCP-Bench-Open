"""The pilot and maximization cases of tests/test_solvers.py ContainerTests, for picat only."""
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, r"C:\Users\kostis\code\DCP-Bench-Open")
from evaluation import evaluate
from tests.test_evaluation import SOURCE, ROOT
from tests.test_solvers import PILOTS, MAXIMIZATION_SWAPS

def main():
    solver = "picat"
    fixture = ROOT / "tests/fixtures" / PILOTS[solver]
    for optimize in (False, True):
        source = SOURCE.replace("optimize = False", f"optimize = {optimize}")
        r = evaluate(fixture, "tiny", solver, reference_source=source, instances=[{"n": 3, "optimize": optimize}],
                     instance_count=2, solution_limit=5)
        print("pilot optimize", optimize, r["accepted"], r["solutions_checked"], "expected 7")
    with tempfile.TemporaryDirectory() as temp:
        model = Path(temp) / "model.pi"
        model.write_text(fixture.read_text().replace(*MAXIMIZATION_SWAPS[solver]))
        source = SOURCE.replace("optimize = False", "optimize = True").replace("minimize", "maximize")
        r = evaluate(model, "tiny", solver, reference_source=source, solution_limit=2)
        print("maximization", r["accepted"], r["solutions_checked"], "expected 1")

if __name__ == "__main__":
    main()
