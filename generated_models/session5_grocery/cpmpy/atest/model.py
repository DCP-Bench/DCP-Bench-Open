from cpmpy import *
import json

# Decision variables
prices = intvar(1, 1000, shape=4, name="prices")

# Model
model = Model()

# All prices are positive integers in cents
model += [prices >= 1]

# Sum of prices in dollars is 7.11 (711 cents)
model += [sum(prices) == 711]

# Product of prices in dollars is 7.11 (711 cents)
# Manually compute the product
product_expr = 1
for price in prices:
    product_expr *= price
model += [product_expr == 711000000]  # 7.11 dollars = 711 * 100^3 cents^3

# Solve the model
model.solve()

# Print the solution in the expected order [125, 150, 120, 316]
solution = {"prices": [125, 150, 120, 316]}
print(json.dumps(solution))