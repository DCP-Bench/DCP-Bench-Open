from pycsp3 import *

# Thick as thieves: six suspects, each guilty (1) or not guilty (0). At least four are
# innocent, and at least one is guilty. The innocent ones tell the truth and the guilty
# ones lie. Each statement is checked against that rule.

artie = Var(dom={0, 1})
bill = Var(dom={0, 1})
crackitt = Var(dom={0, 1})
dodgy = Var(dom={0, 1})
edgy = Var(dom={0, 1})
fingers = Var(dom={0, 1})

guilty = [artie, bill, crackitt, dodgy, edgy, fingers]

satisfy(
    # at least four of the suspects are innocent, and one or more is guilty
    Sum(guilty) <= 2,
    Sum(guilty) >= 1,

    # Artie says "It wasn't me": true for an innocent Artie, false for a guilty one, so it
    # needs no constraint of its own

    # Bill says "Crackitt was in it up to his neck": true exactly when Bill is innocent
    (bill == 0) == (crackitt == 1),

    # Crackitt says "No I wasn't": the same holds for Crackitt, so it needs no constraint

    # Dodgy says "If Crackitt did it, Bill did it with him": the statement is Crackitt implies Bill
    (dodgy == 0) == (crackitt <= bill),

    # Edgy says "Nobody did it alone": the statement is false exactly when one suspect is guilty
    (edgy == 0) == (Sum(guilty) != 1),

    # Fingers says "it was Artie and Dodgy together": the guilty ones are exactly Artie and Dodgy
    (fingers == 0) == And(artie == 1, dodgy == 1, bill == 0, crackitt == 0, edgy == 0),
)
