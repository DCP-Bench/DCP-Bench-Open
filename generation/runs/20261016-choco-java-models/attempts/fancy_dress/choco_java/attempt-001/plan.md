# Plan: fancy dress (fancy_dress)

- green tie t, green hat h, green shirt r, green socks s, entrance fee n, all 0/1
- he owns a green shirt and wears it -> r = 1 (no shirt cost)
- 1: if someone wears a green tie he has to wear a green shirt -> t <= r
- 2: green socks and a green shirt only if a green tie or a green hat -> s + r - t - h <= 1
- 3: a green shirt or a green hat or no green socks needs a green tie -> t = 1 or (r = 0, h = 0, s = 1)
- 4: not dressed according to rules 1-3 pays 11 -> rules 1-3 hold <=> n = 0 (reified)
- costs: tie 10, hat 2, socks 12, fee 11 -> cost = 10t + 2h + 12s + 11n
- objective: minimize cost
- outputs: t, h, r, s, n
