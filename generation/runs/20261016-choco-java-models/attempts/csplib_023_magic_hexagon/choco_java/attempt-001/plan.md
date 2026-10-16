# Plan: magic hexagon (csplib_023)

- arrange the numbers 1 to 19 in the hexagon (cells A..S, rows A B C / D E F G / H I J K L / M N O P / Q R S) -> one IntVar per cell, domain 1..NUM_CELLS (from the instance), output in order A..S
- each number is used once -> m.allDifferent(cell, "AC").post()
- each of the 15 lines sums to the magic constant (38) -> m.sum(line, "=", MAGIC_SUM).post() per line
  - 5 rows: ABC, DEFG, HIJKL, MNOP, QRS
  - 5 lines down to the right: HMQ, DIRN, AEJOS, BFKP, CGL
  - 5 lines down to the left: ADH, BEIM, CFJNQ, GKOR, LPS
- objective: none (satisfaction)
