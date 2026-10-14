from pycsp3 import *

# buy 100 fruits, spending 100 dollars, with every type bought at least once
# prices are scaled by 315 (the lcm of the pack sizes) to keep the coefficients integer
# bananas: 5 for 3 dollars, oranges: 7 for 5 dollars, mangoes: 9 for 7 dollars, apples: 3 for 9 dollars
bananas = Var(dom=range(1, 101))
oranges = Var(dom=range(1, 101))
mangoes = Var(dom=range(1, 101))
apples = Var(dom=range(1, 101))

satisfy(
    # the number of fruits bought must be 100
    bananas + oranges + mangoes + apples == 100,
    # the total price must be 100 dollars, scaled by 315
    189 * bananas + 225 * oranges + 245 * mangoes + 945 * apples == 100 * 315,
)

# bananas and apples should be bought in the smallest quantity possible
minimize(bananas + apples)
