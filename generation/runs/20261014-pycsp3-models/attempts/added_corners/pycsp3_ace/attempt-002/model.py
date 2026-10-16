# Problem: Place the digits 1 to 8 in the added-corners diagram so each square holds the sum of its two adjoining circles.
from pycsp3 import *

# Enter the digits 1 through 8 in the circles and squares.
# Layout (reading order): top-left C, top F, top-right C, left F, right F, bottom-left C, bottom F, bottom-right C.
positions = VarArray(size=8, dom=range(1, 9))
tl, tm, tr, ml, mr, bl, bm, br = positions
satisfy(
    # all digits are used once
    AllDifferent(positions),
    # the number in each square is the sum of the adjoining circles
    tm == tl + tr,
    ml == tl + bl,
    mr == tr + br,
    bm == bl + br,
)
