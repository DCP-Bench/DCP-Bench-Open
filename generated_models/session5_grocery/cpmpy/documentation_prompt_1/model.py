
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# Prices in cents, assume reasonable range 1 to 711 (since sum is 711 cents)
prices = cp.intvar(1, 711, shape=4, name="prices")

# Constraints
# Sum of prices is 711 cents ($7.11)
model += (cp.sum(prices) == 711)

# Product of prices is 71100  (7.11 dollars = 711 cents, product is 7.11 dollars in cents^4)
# The product is 7.11 dollars, but since prices are in cents, product is 7.11^4 in cents^4
# Actually, the problem states the product of the four prices is also 7.11 dollars.
# But the problem states the cashier multiplied the four items instead of adding them and got 7.11 dollars.
# So the product of the four prices in dollars is 7.11.
# Since prices are in cents, product in cents^4 = 7.11 * 100^4 = 7.11 * 100000000 = 711000000
# But this is too large for integer variables.
# Instead, we can keep prices in cents and product in cents^4, but this is too large.
# Alternative: prices in cents, product in cents^4 = 711000000
# We can use cp.Element or cp.Prod, but cpmpy does not have direct product constraint.
# We can use a helper variable for product and constrain it.

# Define product variable
product = cp.intvar(1, 10**9, name="product")

# Constraint for product
model += (product == prices[0] * prices[1] * prices[2] * prices[3])

# Product must be 711000000 (7.11 * 100^4)
model += (product == 711000000)

# Solve and print
if model.solve():
    solution = {'prices': prices.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
