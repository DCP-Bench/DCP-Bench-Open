from cpmpy import *
import json

# Decision variables
oranges = intvar(0, 100, name="oranges")
bananas = intvar(0, 100, name="bananas")
mangoes = intvar(0, 100, name="mangoes")
apples = intvar(0, 100, name="apples")

# Model
model = Model()

# Total number of fruits is 100
model += [oranges + bananas + mangoes + apples == 100]

# Total cost is 100 dollars (correct cost per fruit)
model += [3/5 * bananas + 5/7 * oranges + 7/9 * mangoes + 3 * apples == 100]

# All types of fruits must be purchased (at least one of each)
model += [oranges >= 1]
model += [bananas >= 1]
model += [mangoes >= 1]
model += [apples >= 1]

# Bananas and apples should be of minimum quantity
# Use constraints to enforce bananas and apples are the smallest
model += [bananas <= oranges]
model += [bananas <= mangoes]
model += [bananas <= apples]
model += [apples <= oranges]
model += [apples <= mangoes]
model += [apples <= bananas]

# Solve the model
model.solve()

# Print the solution
solution = {
    "oranges": oranges.value(),
    "bananas": bananas.value(),
    "apples": apples.value(),
    "mangoes": mangoes.value()
}
print(json.dumps(solution))