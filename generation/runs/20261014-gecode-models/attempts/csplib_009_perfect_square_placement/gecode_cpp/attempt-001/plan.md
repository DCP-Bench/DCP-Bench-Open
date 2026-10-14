Place the squares (sides[i]) inside the base x base square without overlap, all borders parallel to the big square's.
  each square's left coordinate x_i in 0..base - side_i -> IntVar(*this, 0, base - s_i) (domain from instance field base and sides)
  each square's bottom coordinate y_i in 0..base - side_i -> same
  no two squares overlap -> nooverlap(*this, x, sides, y, sides, IPL_DOM)
  squares fill the packing square exactly (no spare capacity): redundant on each axis -> cumulative(*this, base, x, sides, sides) and cumulative(*this, base, y, sides, sides)
  Output x_coords, y_coords: the lower-left corners, starting from 0 -> output("x_coords", x), output("y_coords", y)
  Branching: x and y, largest squares first (INT_VAR_SIZE_MIN on the variables, INT_VAL_MIN)
  Objective: none (satisfaction)
