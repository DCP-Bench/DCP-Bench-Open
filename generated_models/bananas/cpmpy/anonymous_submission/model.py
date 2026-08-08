from cpmpy import *
import json

# Parameters
total_fruits = 100
total_dollars = 100

# Decision Variables
bananas = intvar(0, total_fruits, name="bananas")
oranges = intvar(0, total_fruits, name="oranges")
mangoes = intvar(0, total_fruits, name="mangoes")
apples = intvar(0, total_fruits, name="apples")

# Model
model = Model()

# Constraints
# Fruit quantity must be exact multiples of their bundle sizes
model += (bananas % 5) == 0
model += (oranges % 7) == 0
model += (mangoes % 9) == 0
model += (apples % 3) == 0

# Total fruits and dollars constraints
model += bananas + oranges + mangoes + apples == total_fruits
model += (3 * (bananas // 5)) + (5 * (oranges // 7)) + (7 * (mangoes // 9)) + (9 * (apples // 3)) == total_dollars

# All types must be purchased (at least 1 fruit each)
model += bananas >= 1
model += oranges >= 1
model += mangoes >= 1
model += apples >= 1

# Minimize disliked fruits (bananas and apples)
disliked_fruits = bananas + apples
model.minimize(disliked_fruits)

# Solve
model.solve()

# Print solution
solution = {
    "bananas": bananas.value(),
    "oranges": oranges.value(),
    "mangoes": mangoes.value(),
    "apples": apples.value()
}
print(json.dumps(solution))