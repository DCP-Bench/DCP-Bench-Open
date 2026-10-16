Fill the grid with the digits 1 through 6 -> x[r][c] in 1..n
Each row contains exactly one of each digit -> allDifferent(row, "AC") for each row
Each column contains exactly one of each digit -> allDifferent(column, "AC") for each column
Each cage achieves the specified result using one of + - x / (digits may repeat) -> per cage, a disjunction over the operations that fit its size: single cell = value; two cells: sum, difference, product or exact quotient; larger cages: sum or product; posted as sum(option Booleans) >= 1
The instance does not name the operation of each cage, so each cage's operation is a choice -> the Boolean options above
Print the solved grid (x) -> output x
Objective: none (satisfaction)
