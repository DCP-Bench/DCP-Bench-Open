from pysmt.shortcuts import INT, And, Equals, GE, Int, LE, Plus, Solver, Symbol, Times
import json

# Decision variables: number of men, women, and children
men = Symbol("men", INT)
women = Symbol("women", INT)
children = Symbol("children", INT)

formula = And(
    GE(men, Int(0)), LE(men, Int(100)),
    GE(women, Int(0)), LE(women, Int(100)),
    GE(children, Int(0)), LE(children, Int(100)),
    # 100 people in total
    Equals(Plus(men, women, children), Int(100)),
    # 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
    Equals(Plus(Times(Int(6), men), Times(Int(4), women), children), Int(200)),
    # Five times as many women as men
    Equals(women, Times(Int(5), men)),
)

with Solver(name="z3") as solver:
    solver.add_assertion(formula)
    if not solver.solve():
        raise SystemExit("No solution found.")
    print(json.dumps({
        "men": int(solver.get_value(men).constant_value()),
        "women": int(solver.get_value(women).constant_value()),
        "children": int(solver.get_value(children).constant_value()),
    }))
