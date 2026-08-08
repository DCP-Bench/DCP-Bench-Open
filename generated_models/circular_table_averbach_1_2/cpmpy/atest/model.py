from cpmpy import *
import json

# Parameters
n_nationalities = 3  # American, English, French

# Decision variables
x = intvar(0, n_nationalities - 1, name="x")  # Nationality of X
y = intvar(0, n_nationalities - 1, name="y")  # Nationality of Y
z = intvar(0, n_nationalities - 1, name="z")  # Nationality of Z
american = intvar(0, n_nationalities - 1, name="american")  # Person who is American
english = intvar(0, n_nationalities - 1, name="english")  # Person who is English
french = intvar(0, n_nationalities - 1, name="french")  # Person who is French

# Model
model = Model()

# Each person has a unique nationality
model += [AllDifferent([x, y, z])]

# Each nationality is assigned to exactly one person
model += [AllDifferent([american, english, french])]

# Y passed three hearts to the American
model += [y != american]

# X passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman
# This implies a circular seating: X -> A -> French
# So, the person to the right of X is the one who passes to the French person
# In a circular arrangement of 3 people, the right of X is (X + 1) % 3
# The right of that person is (X + 2) % 3, who is the French person
model += [(french == (x + 2) % 3)]

# Solve the model
model.solve()

# Print the solution
solution = {
    "y": y.value(),
    "english": english.value(),
    "american": american.value(),
    "french": french.value(),
    "x": x.value(),
    "z": z.value()
}
print(json.dumps(solution))