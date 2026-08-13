import clyngor
import gc
import json
import sys

ASP = """
% Decision variables: number of men, women, and children
% men ≤ 20 because five times as many women as men and 100 people
{ m(0..20) } = 1.
{ w(0..100) } = 1.
{ c(0..100) } = 1.

% Five times as many women as men
:- m(M), w(W), W != 5 * M.
% 100 people in total
:- m(M), w(W), c(C), M + W + C != 100.
% 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
:- m(M), w(W), c(C), 6 * M + 4 * W + C != 200.

#show m/1.
#show w/1.
#show c/1.
"""

solver = clyngor.Solver(backend="module")
answers = clyngor.solve(inline=ASP, nb_model=1, solver=solver)
answer = next(iter(answers), None)
if answer is None:
    raise SystemExit("No solution found.")
parsed = {name: args[0] for name, args in answer}
if set(parsed) != {"m", "w", "c"}:
    raise SystemExit("No solution found.")
print(json.dumps({
    "men": parsed["m"],
    "women": parsed["w"],
    "children": parsed["c"],
}))
sys.stdout.flush()
del answers
del solver
gc.collect()
