Tommy was given 15 coins (half-crowns, shillings and sixpence) -> linear(*this, coins, IRT_EQ, 15) with coins = [half_crowns, shillings, sixpences]  (count row: sum of coins is a weighted count, linear over the coin counts)
he had £1 5s 6d = 306 pence -> linear(*this, IntArgs({30,12,6}), coins, IRT_EQ, 306, IPL_DOM) (half-crown 30 pence, shilling 12, sixpence 6)
the coins given are half-crowns, shillings and sixpence, so each kind occurs at least once -> domains 1..15 (no decomposition needed)
branching -> branch(*this, coins, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
objective -> none (satisfaction); output half_crowns = the half-crown count
