from cpmpy import *
import json

# Decision Variables
paper_hanger = intvar(0, 10000, name="paper_hanger")  # Cost in dollars
painter = intvar(0, 10000, name="painter")           # Cost in dollars
plumber = intvar(0, 10000, name="plumber")           # Cost in dollars
electrician = intvar(0, 10000, name="electrician")   # Cost in dollars
carpenter = intvar(0, 10000, name="carpenter")       # Cost in dollars
mason = intvar(0, 10000, name="mason")               # Cost in dollars

# Model
model = Model()

# Constraints based on given payment pairs
model += (paper_hanger + painter == 1100)
model += (painter + plumber == 1700)
model += (plumber + electrician == 1100)
model += (electrician + carpenter == 3300)
model += (carpenter + mason == 5300)
model += (mason + painter == 3200)

# Solve
model.solve()

# Print solution
solution = {
    "paper_hanger": paper_hanger.value(),
    "painter": painter.value(),
    "plumber": plumber.value(),
    "electrician": electrician.value(),
    "carpenter": carpenter.value(),
    "mason": mason.value()
}
print(json.dumps(solution))
# End of CPMPy script