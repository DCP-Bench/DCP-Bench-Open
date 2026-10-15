# chess_set plan (attempt-001)

- how many small sets are made each week -> small = unary count of Bools, bound 53 (from lathe hours 160 / 3 h)
- how many large sets are made each week -> large = unary count of Bools, bound 66 (from boxwood 200 kg / 3 kg)
- small set needs 3 hours on a lathe, large set 2 hours; 160 lathe-hours per week -> 3*small + 2*large <= 160
- small set needs 1 kg boxwood, large set 3 kg; 200 kg per week -> small + 3*large <= 200
- maximise profit: small set $5, large set $20 -> maximize 5*small + 20*large (same expression as max_profit)
