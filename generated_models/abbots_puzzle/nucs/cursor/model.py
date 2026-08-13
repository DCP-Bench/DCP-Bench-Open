from nucs.problems.problem import Problem
from nucs.propagators.propagators import ALG_LINEAR_EQ_C
from nucs.solvers.backtrack_solver import BacktrackSolver
import json

# Decision variables: number of men, women, and children
problem = Problem([(0, 100), (0, 100), (0, 100)])
# 100 people in total
problem.add_propagator(ALG_LINEAR_EQ_C, [0, 1, 2], [1, 1, 1, 100])
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
problem.add_propagator(ALG_LINEAR_EQ_C, [0, 1, 2], [6, 4, 1, 200])
# Five times as many women as men
problem.add_propagator(ALG_LINEAR_EQ_C, [0, 1], [5, -1, 0])

solver = BacktrackSolver(problem)
solution = next(solver.solve(), None)
if solution is None:
    raise SystemExit("No solution found.")

print(json.dumps({
    "men": int(solution[0]),
    "women": int(solution[1]),
    "children": int(solution[2]),
}))
