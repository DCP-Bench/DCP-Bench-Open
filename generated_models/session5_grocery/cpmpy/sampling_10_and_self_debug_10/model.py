
import cpmpy as cp
import json

# Precompute all quadruples (p1, p2, p3, p4) with:
# 1 <= p1 <= p2 <= p3 <= p4 <= 711
# sum = 711
# product = 711000000

# To reduce search space, note that prices are integers in cents.

table = []
target_sum = 711
target_product = 711000000

# Since the product is large, and the numbers are small, we can try to generate candidates efficiently.

# To speed up, we can iterate p1, p2, p3 and compute p4 = 711 - (p1+p2+p3)
# Then check ordering and product.

for p1 in range(1, 712):
    for p2 in range(p1, 712):
        for p3 in range(p2, 712):
            p4 = target_sum - (p1 + p2 + p3)
            if p4 < p3 or p4 > 711:
                continue
            # Check product
            prod = p1 * p2 * p3 * p4
            if prod == target_product:
                table.append([p1, p2, p3, p4])

# Model definition
model = cp.Model()

# Decision Variables
prices = cp.intvar(1, 711, shape=4, name="prices")

# Table constraint
model += cp.Table(prices, table)

# Solve and print
if model.solve():
    solution = {'prices': prices.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
