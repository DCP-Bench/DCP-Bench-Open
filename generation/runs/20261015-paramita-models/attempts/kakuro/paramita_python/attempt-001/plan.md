Fill each white cell with a digit from 1 to 9 -> one-hot Bools xv[cell][v], sum(xv[cell].values()) == 1 per white cell
Black cells and clue cells print 0 -> constant 0 in output x
The sum of the numbers in each entry matches its clue -> sum(v * xv[c][v] for c in entry for v in 1..9) == clue
No digit is duplicated in any entry -> per entry and digit v: sum(xv[c][v] for c in entry) <= 1
Print the solution matrix x as a list of lists of integers 0..9 -> x[r][c] = sum(v * xv[(r,c)][v]) for white cells, 0 otherwise
Objective: none (satisfaction)
