An order m quasigroup is a Latin square of size m: values 0..m-1, each value once per row and column.
  "each element occurs once in every row and column" -> allDifferent per row and per column, "AC"
  "a m x m multiplication table" -> quasigroup[a][b] = a*b, IntVar[m][m] domain 0..m-1
  "QG3.m: (a*b)*(b*a) = a for all a, b" -> let ab = q[a][b], ba = q[b][a]; q[ab][ba] = a
      -> element over the flattened table at index ab*m+ba (m.element with IntVar index, offset 0), result equal to a
Objective: none (satisfaction).
