Arrange the numbers 1 to 12 on the clock face
  -> X[i][v] one-hot Bool (position i holds value v); x[i] = sum v*X[i][v]
Each position holds exactly one number
  -> sum_v X[i][v] == 1
Each number is used exactly once around the clock
  -> sum_i X[i][v] == 1
No triplet of adjacent numbers has a sum higher than 21 (clock wraps around)
  -> x[i] + x[i+1] + x[i+2] <= 21 for i in 0..11, indices mod 12
Output x: the 12 position values
  -> list of the 12 integer expressions x[i]
Objective: none (satisfaction)
