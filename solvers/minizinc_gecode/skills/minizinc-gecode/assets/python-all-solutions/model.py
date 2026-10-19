"""Python all_solutions counts a free auxiliary variable as a separate solution.

Here x is the only output, and aux is a helper that nothing constrains.
Python enumerates every variable, so each value of x appears once per value
of aux. Keeping only the distinct values of x gives the answer the CLI prints.
"""
from minizinc import Instance, Model, Solver

MODEL = """
var 1..3: x;
var 0..1: aux;
constraint x <= 2;
solve satisfy;
"""

model = Model()
model.add_string(MODEL)
instance = Instance(Solver.lookup("gecode"), model)
result = instance.solve(all_solutions=True)

solutions = result.solution or []      # a list; empty when there is no solution
print("solutions counted by Python:", len(solutions))
distinct = sorted({s.x for s in solutions})
print("distinct values of x:", distinct)
