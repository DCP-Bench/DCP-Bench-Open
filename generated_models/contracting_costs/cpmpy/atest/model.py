from cpmpy import *
import json

# Decision variables
painter = intvar(0, 10000, name="painter")
plumber = intvar(0, 10000, name="plumber")
electrician = intvar(0, 10000, name="electrician")
carpenter = intvar(0, 10000, name="carpenter")
mason = intvar(0, 10000, name="mason")
paper_hanger = intvar(0, 10000, name="paper_hanger")

# Model
model = Model()

# Constraints based on the problem description
model += [painter + paper_hanger == 1100]
model += [painter + plumber == 1700]
model += [plumber + electrician == 1100]
model += [electrician + carpenter == 3300]
model += [carpenter + mason == 5300]
model += [mason + painter == 3200]

# Solve the model
model.solve()

# Print the solution in the correct order
solution = {
    "paper_hanger": paper_hanger.value(),
    "painter": painter.value(),
    "plumber": plumber.value(),
    "electrician": electrician.value(),
    "carpenter": carpenter.value(),
    "mason": mason.value()
}
print(json.dumps(solution))