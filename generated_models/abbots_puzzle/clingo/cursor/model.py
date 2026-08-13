from clingo import Control
import json

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

ctl = Control()
ctl.add("base", [], ASP)
ctl.ground([("base", [])])
solution = {}


def on_model(model):
    for atom in model.symbols(shown=True):
        if atom.name in ("m", "w", "c") and atom.arguments:
            solution[atom.name] = atom.arguments[0].number


if not ctl.solve(on_model=on_model).satisfiable or set(solution) != {"m", "w", "c"}:
    raise SystemExit("No solution found.")
print(json.dumps({
    "men": solution["m"],
    "women": solution["w"],
    "children": solution["c"],
}))
