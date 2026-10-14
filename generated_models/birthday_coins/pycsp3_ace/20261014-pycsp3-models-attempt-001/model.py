from pycsp3 import *

# Tommy was given 15 coins: half-crowns, shillings and sixpences, adding up to one pound 5 shillings 6 pence
# number of half-crowns given
half_crowns = Var(dom=range(16))
# number of shillings given
shillings = Var(dom=range(16))
# number of sixpences given
sixpences = Var(dom=range(16))
satisfy(
    # he was given 15 coins in total
    half_crowns + shillings + sixpences == 15,
    # the coins add up to one pound 5 shillings 6 pence, which is 306 pence
    # (a half-crown is 30 pence, a shilling 12 pence, a sixpence 6 pence)
    30 * half_crowns + 12 * shillings + 6 * sixpences == 306,
)
