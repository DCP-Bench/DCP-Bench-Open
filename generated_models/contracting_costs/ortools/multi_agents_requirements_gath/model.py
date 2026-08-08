"""Solve the tradesmen-fee puzzle with Google OR-Tools CP-SAT.

The six pairwise sums are translated into linear equality constraints.
The program prints ONE JSON line whose keys are exactly
['painter', 'plumber', 'electrician', 'carpenter', 'mason', 'paper_hanger'].
"""

from ortools.sat.python import cp_model
import json

# ---------------------------------------------------------------------------
# Constant data (pairwise totals, taken verbatim from the story)
# ---------------------------------------------------------------------------
TOTAL_PH_PA = 1100  # paper-hanger + painter
TOTAL_PA_PL = 1700  # painter + plumber
TOTAL_PL_EL = 1100  # plumber + electrician
TOTAL_EL_CA = 3300  # electrician + carpenter
TOTAL_CA_MA = 5300  # carpenter + mason
TOTAL_MA_PA = 3200  # mason + painter


def main() -> None:
    model = cp_model.CpModel()

    # A single fee cannot exceed the largest pair total.
    MAX_FEE = TOTAL_CA_MA  # 5 300

    # -------------------------------------------------------------------
    # Decision variables: positive integers (fees in whole dollars)
    # -------------------------------------------------------------------
    paper_hanger = model.NewIntVar(1, MAX_FEE, "paper_hanger")
    painter      = model.NewIntVar(1, MAX_FEE, "painter")
    plumber      = model.NewIntVar(1, MAX_FEE, "plumber")
    electrician  = model.NewIntVar(1, MAX_FEE, "electrician")
    carpenter    = model.NewIntVar(1, MAX_FEE, "carpenter")
    mason        = model.NewIntVar(1, MAX_FEE, "mason")

    # -------------------------------------------------------------------
    # Hard constraints – the six given equations
    # -------------------------------------------------------------------
    model.Add(paper_hanger + painter     == TOTAL_PH_PA)
    model.Add(painter      + plumber     == TOTAL_PA_PL)
    model.Add(plumber      + electrician == TOTAL_PL_EL)
    model.Add(electrician  + carpenter   == TOTAL_EL_CA)
    model.Add(carpenter    + mason       == TOTAL_CA_MA)
    model.Add(mason        + painter     == TOTAL_MA_PA)

    # Pure feasibility model – no objective.

    # -------------------------------------------------------------------
    # Solve
    # -------------------------------------------------------------------
    solver = cp_model.CpSolver()

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # According to the maths the system HAS a unique solution, but guard anyway.
        print(json.dumps({"error": "No solution found"}))
        return

    # -------------------------------------------------------------------
    # Output – JSON with the exact key order required by the checker
    # -------------------------------------------------------------------
    result = {
        "painter":      solver.Value(painter),
        "plumber":      solver.Value(plumber),
        "electrician":  solver.Value(electrician),
        "carpenter":    solver.Value(carpenter),
        "mason":        solver.Value(mason),
        "paper_hanger": solver.Value(paper_hanger),
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
