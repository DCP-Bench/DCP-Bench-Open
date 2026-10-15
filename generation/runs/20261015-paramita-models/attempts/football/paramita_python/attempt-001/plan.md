# Plan: football

Prices are in GBP thousands (integers), so z is an integer sum and the budget is 30000.

- "Goalkeepers (must buy 1 exactly)" -> one Bool per player; `sum(goalkeepers) == 1`
- "Defenders (must buy 2 or more)" -> `sum(defenders) >= 2`
- "Midfielders (must buy 3 or more)" -> `sum(midfielders) >= 3`
- "Strikers (must buy 2 or more)" -> `sum(strikers) >= 2`
- "you must buy at least eleven players in total" -> `sum(all players) >= 11`
- "upper limit of GBP 30 million" -> `sum(price * bought) <= 30000` (PB, weights up to 9500)
- "spend as much money as you can" / "total price z" -> maximise `z = sum(price * bought)`
