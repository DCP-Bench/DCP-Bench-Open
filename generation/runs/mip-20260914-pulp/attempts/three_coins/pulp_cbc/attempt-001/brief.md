# three_coins
Instance: `num_moves`, `init`. Output: `steps` — a (num_moves + 1) x len(init)
0/1 matrix. The first row is the initial configuration, each move flips exactly
one coin, and the last row is all heads or all tails.
The per-coin difference is an exclusive or of two binaries, written with the
four inequalities that pin it exactly.
