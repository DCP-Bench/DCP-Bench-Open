# Plan: diet

- "the prices and the nutritional requirements (at least) for each nutrition type" -> instance fields price[j] and limits[k] (k = calories, chocolate, sugar, fat).
- "Type of Food ... Calories Chocolate Sugar Fat" table -> constant nutrient matrix nut[k][j] (problem constant, from the description).
- "how many units of each food" -> per food j, unary (order) Bools x_j_ge_v for v in 1..ub_j; units = sum of those Bools. The bound ub_j = max over k with nut[k][j] > 0 of ceil(limits[k] / nut[k][j]) (derived: removing one unit beyond that never breaks a requirement and never raises cost).
- "at least" each requirement -> sum_j nut[k][j] * units_j >= limits[k], one PB constraint per nutrient.
- "minimize the cost of the products" -> objective sum_j price[j] * units_j (minimize); output cost is the same expression.
