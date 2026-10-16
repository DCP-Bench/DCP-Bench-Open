Spend as much money as you can -> objective: maximize z, the total price (GBP thousands) of the players bought.
The chairman gives an upper limit of GBP 30 million -> m.scalar(players, price_k, "<=", 30000), prices in thousands.
Goalkeepers: must buy 1 exactly -> m.sum(goalkeepers, "=", 1).
Defenders: must buy 2 or more -> m.sum(defenders, ">=", 2).
Midfielders: must buy 3 or more -> m.sum(midfielders, ">=", 3).
Strikers: must buy 2 or more -> m.sum(strikers, ">=", 2).
At least eleven players in total -> m.sum(all players, ">=", 11).
Total price of the selected players -> z = m.scalar(players, price_k, "=", z).
