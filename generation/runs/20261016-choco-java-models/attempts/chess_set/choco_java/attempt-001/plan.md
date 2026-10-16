# Plan: weekly production of small and large boxwood chess sets (chess_set)

- "small set requires 3 hours on a lathe, large set 2 hours; four lathes, 40 hours each, so 160 lathe-hours" -> scalar(small, large; 3, 2) <= 160
- "small set requires 1 kg of boxwood, large set 3 kg; only 200 kg per week" -> scalar(small, large; 1, 3) <= 200
- "small set profit $5, large set profit $20" -> profit = scalar(small, large; 5, 20)
- "maximise profit" -> setObjective(MAXIMIZE, profit)
- "print small_set, large_set, max_profit" -> outputs small, large, profit
- instance fields: none (all data is in the description)
