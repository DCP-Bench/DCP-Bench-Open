
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: costs for each craftsman in dollars
paper_hanger = cp.intvar(0, 10000, name="paper_hanger")
painter      = cp.intvar(0, 10000, name="painter")
plumber      = cp.intvar(0, 10000, name="plumber")
electrician  = cp.intvar(0, 10000, name="electrician")
carpenter    = cp.intvar(0, 10000, name="carpenter")
mason        = cp.intvar(0, 10000, name="mason")

# Constraints based on the pairwise payments
model += [
    paper_hanger + painter     == 1100,
    painter      + plumber     == 1700,
    plumber      + electrician == 1100,
    electrician  + carpenter   == 3300,
    carpenter    + mason       == 5300,
    mason        + painter     == 3200
]

# Solve and print
if model.solve():
    solution = {
        'paper_hanger': int(paper_hanger.value()),
        'painter':      int(painter.value()),
        'plumber':      int(plumber.value()),
        'electrician':  int(electrician.value()),
        'carpenter':    int(carpenter.value()),
        'mason':        int(mason.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
