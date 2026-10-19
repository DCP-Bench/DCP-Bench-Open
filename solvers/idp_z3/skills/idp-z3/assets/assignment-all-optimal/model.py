"""Assign 3 workers to 3 tasks at minimum total cost, and list every optimal assignment."""
from idp_engine import IDP, Theory

cost = [[2, 2, 3],
        [2, 2, 3],
        [3, 3, 1]]

KB = """
vocabulary V {
    type Worker <: Int
    type Task <: Int
    cost: Worker * Task -> Int
    does: Worker * Task -> Bool
    total: () -> Int
}
theory T: V {
    // every worker does exactly one task, every task gets exactly one worker
    ! w in Worker: ?=1 t in Task: does(w, t).
    ! t in Task: ?=1 w in Worker: does(w, t).
    // the objective; aggregates over two variables are fine
    total() = sum{{ cost(w, t) | w in Worker, t in Task: does(w, t) }}.
}
"""

rows, cols = len(cost), len(cost[0])
structure = "structure S: V {\n"
structure += f"    Worker := {{0..{rows - 1}}}.\n    Task := {{0..{cols - 1}}}.\n"
structure += "    cost := {" + ", ".join(f"({w},{t})->{cost[w][t]}"
                                       for w in range(rows) for t in range(cols)) + "}.\n}\n"

kb = IDP.from_str(KB + structure)
theory = Theory(*kb.get_blocks("T, S"))
# optimize() fixes total() to its optimum (it raises AssertionError when nothing is feasible);
# the following expand() then enumerates only optimal models.
theory.optimize("total()", minimize=True)

count = 0
for model in theory.expand(max=0, timeout_seconds=0):
    if isinstance(model, str):
        print(model.strip())
        break
    count += 1
    plan = [next(t for t in range(cols) if str(model[f"does({w}, {t})"].value) == "true")
            for w in range(rows)]
    print(f"optimal {count}: task per worker {plan}, total {model['total()'].value}")
print(f"Optimal assignments: {count}")
