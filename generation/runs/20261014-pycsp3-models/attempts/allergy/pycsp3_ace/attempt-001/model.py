from pycsp3 import *

# Four friends (Debra=0, Janet=1, Hugh=2, Rick=3) each have one surname and one allergy.
# baxter, lemon, malone, fleet give the friend with that surname.
# eggs, mold, nuts, ragweed give the friend with that allergy.
baxter = Var(dom=range(4))
lemon = Var(dom=range(4))
malone = Var(dom=range(4))
fleet = Var(dom=range(4))
eggs = Var(dom=range(4))
mold = Var(dom=range(4))
nuts = Var(dom=range(4))
ragweed = Var(dom=range(4))

satisfy(
    # each surname belongs to a different friend
    AllDifferent([baxter, lemon, malone, fleet]),
    # each allergy belongs to a different friend
    AllDifferent([eggs, mold, nuts, ragweed]),
    # Rick is not allergic to mold
    mold != 3,
    # Baxter is allergic to eggs
    baxter == eggs,
    # Hugh is neither surnamed Lemon nor Fleet
    lemon != 2,
    fleet != 2,
    # Debra is allergic to ragweed
    ragweed == 0,
    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold
    lemon != 1,
    eggs != 1,
    mold != 1,
)
