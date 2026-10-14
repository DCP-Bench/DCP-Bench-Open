# Plan: magic hexagon, 19 cells A..S, 15 lines each summing to MAGIC_SUM

Cells in LD order: A B C / D E F G / H I J K L / M N O P / Q R S (LD[0..18]).
- the numbers 1 to 19 are all different, one per cell -> distinct(*this, LD, IPL_DOM)
- every number from 1 to NUM_CELLS is used once (domain of each cell 1..NUM_CELLS) -> IntVarArray domain 1..NUM_CELLS, covered by distinct over n cells
- the 3 horizontal rows A B C, D E F G, H I J K L, M N O P, Q R S sum to the magic constant -> linear(*this, row, IRT_EQ, MAGIC_SUM, IPL_DOM)
- the 5 down-left diagonals A D H, B E I M, C F J N Q, G K O R, L P S sum to the magic constant -> linear(..., IPL_DOM)
- the 5 down-right diagonals C G L, B F K P, A E J O S, D I N R, H M Q sum to the magic constant -> linear(..., IPL_DOM)
- Constraint blocks are one per line direction (15 linear posts). No decomposition needed: linear is the map row for a sum equal to a constant.
- Branching: INT_VAR_SIZE_MIN, INT_VAL_MIN over LD (all decision variables).
- Objective: none (satisfaction). Output LD only.
