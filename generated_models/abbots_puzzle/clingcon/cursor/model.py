from clingo import ast
from clingo.control import Control
from clingcon import ClingconTheory
import json

ASP = """
&sum { m } >= 0. &sum { m } <= 100.
&sum { w } >= 0. &sum { w } <= 100.
&sum { c } >= 0. &sum { c } <= 100.
% 100 people in total
&sum { m; w; c } = 100.
% 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
&sum { 6*m; 4*w; c } = 200.
% Five times as many women as men
&sum { w; -5*m } = 0.
&show { m; w; c }.
"""

theory = ClingconTheory()
ctl = Control(["--warn=none"])
theory.register(ctl)
with ast.ProgramBuilder(ctl) as bld:
    ast.parse_string(ASP, lambda stm: theory.rewrite_ast(stm, bld.add))
ctl.ground([("base", [])])
theory.prepare(ctl)

solution = {}


def on_model(model):
    theory.on_model(model)
    for symbol, val in theory.assignment(model.thread_id):
        solution[str(symbol)] = int(val)


result = ctl.solve(on_model=on_model)
if not result.satisfiable or set(solution) < {"m", "w", "c"}:
    raise SystemExit("No solution found.")

print(json.dumps({
    "men": solution["m"],
    "women": solution["w"],
    "children": solution["c"],
}))
