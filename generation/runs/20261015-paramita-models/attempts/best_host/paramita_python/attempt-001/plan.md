six seats for your guests -> six seats in a round table, positions 0..5, seat p next to seat (p+1) mod 6
each guest sits in one seat -> s[g][p] Bools, exactly one per guest: sum over p == 1
each seat holds one guest -> exactly one per seat: sum over g == 1
Andrew will only sit next to Dave and Frank (and the others likewise) -> for each non-neighbour pair (g, h) and seat p: ~(s[g][p] & s[h][p+1 mod 6])
arrangement that minimizes conflict -> zero conflicts is reachable, so the model is satisfaction with no conflict term; output x[p] = sum(g * s[g][p]) is the guest in seat p
