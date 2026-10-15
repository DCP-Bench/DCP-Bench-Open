# Plan: knapsack (attempt-001)

- "decide which items to take in the backpack" -> one Bool per item, x[i] = item i taken (`Bool(f"x_{i}")`)
- "without exceeding the weight capacity of the backpack" -> `sum(w * b) <= capacity` (PB over item Bools)
- "maximize the total value of the items in the backpack" -> objective `("maximize", sum(v * b))`
- "Print which items to take (x) as a list of booleans" -> outputs x = list of the item Bools (length = number of items in the instance)
