Problem: nonogram. Shade cells of an 8x13 grid (1 shaded, 0 empty) so each row and column shows its block sequence.
Row i: the shaded blocks in order must match row_rules[i] (zeros are padding) -> regular(row, automaton of 0* b1 0+ b2 ... 0*)
Column j: the shaded blocks in order must match col_rules[j] -> regular(column, automaton of 0* b1 0+ b2 ... 0*)
Cells are 0/1 -> intVarMatrix board 0..1
Objective: none (satisfaction); output board
