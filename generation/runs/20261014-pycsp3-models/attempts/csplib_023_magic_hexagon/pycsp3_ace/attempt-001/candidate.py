from pycsp3 import *

# Magic hexagon: place the numbers 1 to 19 in the cells A to S of a hexagon, so that the sum of the
# numbers on each of the 15 lines (rows and the two diagonal directions) equals the magic sum 38.
# Cells in order: A B C | D E F G | H I J K L | M N O P | Q R S, as indices 0 to 18.
NUM_CELLS = data.NUM_CELLS
MAGIC_SUM = data.MAGIC_SUM

# LD[k] is the number in cell k (A is LD[0], ..., S is LD[18])
LD = VarArray(size=NUM_CELLS, dom=range(1, NUM_CELLS + 1))

satisfy(
    # the numbers 1 to 19 each appear once in the hexagon
    AllDifferent(LD),

    # the three rows of the hexagon: A B C, D E F G, H I J K L, M N O P, Q R S
    Sum([LD[k] for k in [0, 1, 2]]) == MAGIC_SUM,
    Sum([LD[k] for k in [3, 4, 5, 6]]) == MAGIC_SUM,
    Sum([LD[k] for k in [7, 8, 9, 10, 11]]) == MAGIC_SUM,
    Sum([LD[k] for k in [12, 13, 14, 15]]) == MAGIC_SUM,
    Sum([LD[k] for k in [16, 17, 18]]) == MAGIC_SUM,

    # the lines running down and to the right: H M Q, D I N R, A E J O S, B F K P, C G L
    Sum([LD[k] for k in [7, 12, 16]]) == MAGIC_SUM,
    Sum([LD[k] for k in [3, 8, 13, 17]]) == MAGIC_SUM,
    Sum([LD[k] for k in [0, 4, 9, 14, 18]]) == MAGIC_SUM,
    Sum([LD[k] for k in [1, 5, 10, 15]]) == MAGIC_SUM,
    Sum([LD[k] for k in [2, 6, 11]]) == MAGIC_SUM,

    # the lines running down and to the left: A D H, B E I M, C F J N Q, G K O R, L P S
    Sum([LD[k] for k in [0, 3, 7]]) == MAGIC_SUM,
    Sum([LD[k] for k in [1, 4, 8, 12]]) == MAGIC_SUM,
    Sum([LD[k] for k in [2, 5, 9, 13, 16]]) == MAGIC_SUM,
    Sum([LD[k] for k in [6, 10, 14, 17]]) == MAGIC_SUM,
    Sum([LD[k] for k in [11, 15, 18]]) == MAGIC_SUM,
)
