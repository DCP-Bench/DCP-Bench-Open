KenKen or KEN-KEN is a style of arithmetic and logical puzzle sharing
several characteristics with sudoku. The name comes from Japanese and
is translated as 'square wisdom' or 'cleverness squared'.

The objective is to fill the grid in with the digits 1 through 6 such that:

  * Each row contains exactly one of each digit
  * Each column contains exactly one of each digit
  * Each bold-outlined group of cells is a cage containing digits which
    achieve the specified result using the specified mathematical operation:
      addition (+),
      subtraction (-),
      multiplication (x),
      and division (/).
      (Unlike in Killer sudoku, digits may repeat within a group.)

More complex KenKen problems are formed using the principles described
above but omitting the symbols +, -, x and /, thus leaving them as
yet another unknown to be determined. This is such a problem: `problem` lists
each cage as its result and its cells, each cell being a 1-based [row, column].
A cage of two cells may use any of the four operations, and a larger cage
either addition or multiplication.

Print the solved grid (x) as a list of lists of integers ranging from 1 to 6.
