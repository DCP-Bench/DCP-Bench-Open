from pycsp3 import *

# Seat six guests around a round table so that every pair of neighbours
# get along with each other. Guests are numbered 0 Andrew, 1 Betty, 2 Cara,
# 3 Dave, 4 Erica, 5 Frank.

n = 6

# x[k] is the guest seated at position k of the table
x = VarArray(size=n, dom=range(n))

# the people who get along with each other, in both orders
friends = [
    (0, 3), (0, 5),  # Andrew sits next to Dave and Frank
    (1, 2), (1, 4),  # Betty sits next to Cara and Erica
    (2, 5),          # Cara sits next to Frank
    (3, 4),          # Dave sits next to Erica
]
friends = friends + [(b, a) for (a, b) in friends]

satisfy(
    # each guest sits at exactly one seat
    AllDifferent(x),

    # every pair of guests seated next to each other must get along, around the table
    [Table(scope=[x[k], x[(k + 1) % n]], supports=friends) for k in range(n)],
)
