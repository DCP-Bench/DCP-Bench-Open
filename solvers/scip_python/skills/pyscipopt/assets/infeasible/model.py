# Staffing that cannot be met: two shifts of at most 3 people must cover a demand of 7.
from pyscipopt import Model

m = Model("staffing")
m.hideOutput()
early = m.addVar(vtype="I", lb=0, ub=3, name="early")
late = m.addVar(vtype="I", lb=0, ub=3, name="late")
m.addCons(early + late >= 7, name="demand")
m.setObjective(early + late, "minimize")

m.optimize()
status = m.getStatus()
print("Status:", status)
print("Solutions found:", m.getNSols())
if status == "optimal":
    print("early =", round(m.getVal(early)), "late =", round(m.getVal(late)))
else:
    # never read values here: getVal raises "No solution available"
    try:
        m.getVal(early)
    except Warning as e:
        print("getVal refused:", e)
