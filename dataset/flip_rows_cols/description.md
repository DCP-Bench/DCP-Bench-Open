Given is an array of positive and negative numbers.
You can flip the sign of entire rows and columns, as many of them
as you like. The goal is to make each one of all the rows and columns sum to positive
numbers (or zero), and then to find the solution (there are more than one)
that has the smallest overall sum. So for example, for this array:
   33  30 -10
  -16  19   9
  -17 -12 -14
You could flip the sign for the bottom row to get this array:
  33  30 -10
 -16  19   9
  17  12  14
Now all the rows and columns have positive sums, and the overall total is 108.
But you could instead flip the second and third columns, and the second
row, to get this array:
  33  -30  10
  16   19    9
 -17   12   14
All the rows and columns still total positive, and the overall sum is just
66. So this solution is better (I don't know if it's the best).

Print the signs of rows and columns to minimize the overall sum (row_signs, col_signs), as two lists containing -1/1,
depending on the selected sign for the respective row/column.
