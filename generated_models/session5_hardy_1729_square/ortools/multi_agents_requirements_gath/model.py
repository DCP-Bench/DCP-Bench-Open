# -*- coding: utf-8 -*-
"""
Feasibility model for finding four distinct integers in the range 1..100 such that
    a^2 + b^2 = c^2 + d^2
The script uses Google OR-Tools CP-SAT.  All constraints from the specification are
implemented exactly; the only objective is to obtain any feasible assignment.
The final result is printed as JSON with the mandatory keys ['b', 'd', 'c', 'a'].
"""

import json
from ortools.sat.python import cp_model


def main():
    # ------------------------------------------------------------------
    # 1. Model creation
    # ------------------------------------------------------------------
    model = cp_model.CpModel()

    L, U = 1, 100  # domain limits (inclusive)
    max_square = U * U

    # ------------------------------------------------------------------
    # 2. Decision variables (domains are 1..100)
    # ------------------------------------------------------------------
    a = model.NewIntVar(L, U, 'a')
    b = model.NewIntVar(L, U, 'b')
    c = model.NewIntVar(L, U, 'c')
    d = model.NewIntVar(L, U, 'd')

    # Squares of each variable (auxiliary variables)
    a_sq = model.NewIntVar(L * L, max_square, 'a_sq')
    b_sq = model.NewIntVar(L * L, max_square, 'b_sq')
    c_sq = model.NewIntVar(L * L, max_square, 'c_sq')
    d_sq = model.NewIntVar(L * L, max_square, 'd_sq')

    # ------------------------------------------------------------------
    # 3. Constraint set
    # ------------------------------------------------------------------
    # 3.1 Pairwise distinctness
    model.AddAllDifferent([a, b, c, d])

    # 3.2 Link each variable with its square using a table (allowed assignments)
    square_table = [[i, i * i] for i in range(L, U + 1)]
    model.AddAllowedAssignments([a, a_sq], square_table)
    model.AddAllowedAssignments([b, b_sq], square_table)
    model.AddAllowedAssignments([c, c_sq], square_table)
    model.AddAllowedAssignments([d, d_sq], square_table)

    # 3.3 Equal-sum-of-squares: a^2 + b^2 = c^2 + d^2
    model.Add(a_sq + b_sq == c_sq + d_sq)

    # ------------------------------------------------------------------
    # 4. Objective (none) and solver invocation
    # ------------------------------------------------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0  # soft limit for safety

    status = solver.Solve(model)

    # ------------------------------------------------------------------
    # 5. Output handling – print JSON with required keys only
    # ------------------------------------------------------------------
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result = {
            'b': solver.Value(b),
            'd': solver.Value(d),
            'c': solver.Value(c),
            'a': solver.Value(a),
        }
        print(json.dumps(result))
    else:
        # According to spec, we still need to output something – raise exception
        raise RuntimeError('No feasible solution found.')


if __name__ == '__main__':
    main()
