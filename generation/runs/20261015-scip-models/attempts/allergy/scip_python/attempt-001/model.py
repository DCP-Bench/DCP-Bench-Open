# Allergy puzzle: match four friends with their surnames and their allergies.
from pyscipopt import Model, quicksum

# Friends are numbered Debra = 0, Janet = 1, Hugh = 2, Rick = 3.
# Allergies are numbered eggs = 0, mold = 1, nuts = 2, ragweed = 3.
# Surnames are numbered Baxter = 0, Lemon = 1, Malone = 2, Fleet = 3.
FRIENDS = range(4)
FOODS = range(4)
SURNAMES = range(4)
DEBRA, JANET, HUGH, RICK = 0, 1, 2, 3
EGGS, MOLD, NUTS, RAGWEED = 0, 1, 2, 3
BAXTER, LEMON, MALONE, FLEET = 0, 1, 2, 3


def build(instance):
    m = Model()

    # allergy[p, f] = 1 if friend p is allergic to food f
    allergy = {(p, f): m.addVar(name=f"allergy_{p}_{f}", vtype="B") for p in FRIENDS for f in FOODS}
    # surname[p, s] = 1 if friend p has surname s
    surname = {(p, s): m.addVar(name=f"surname_{p}_{s}", vtype="B") for p in FRIENDS for s in SURNAMES}

    # each friend has exactly one allergy
    for p in FRIENDS:
        m.addCons(quicksum(allergy[p, f] for f in FOODS) == 1)
    # each allergy belongs to exactly one friend
    for f in FOODS:
        m.addCons(quicksum(allergy[p, f] for p in FRIENDS) == 1)
    # each friend has exactly one surname
    for p in FRIENDS:
        m.addCons(quicksum(surname[p, s] for s in SURNAMES) == 1)
    # each surname belongs to exactly one friend
    for s in SURNAMES:
        m.addCons(quicksum(surname[p, s] for p in FRIENDS) == 1)

    # Rick is not allergic to mold
    m.addCons(allergy[RICK, MOLD] == 0)

    # Baxter is allergic to eggs: whoever is surnamed Baxter is allergic to eggs, and the reverse
    for p in FRIENDS:
        m.addCons(surname[p, BAXTER] == allergy[p, EGGS])

    # Hugh is neither surnamed Lemon nor Fleet
    m.addCons(surname[HUGH, LEMON] == 0)
    m.addCons(surname[HUGH, FLEET] == 0)

    # Debra is allergic to ragweed
    m.addCons(allergy[DEBRA, RAGWEED] == 1)

    # Janet is not surnamed Lemon
    m.addCons(surname[JANET, LEMON] == 0)
    # Janet is neither allergic to eggs nor to mold
    m.addCons(allergy[JANET, EGGS] == 0)
    m.addCons(allergy[JANET, MOLD] == 0)

    # The outputs give, for each food and surname, the friend's index (Debra = 0 ... Rick = 3).
    outputs = {
        "eggs": quicksum(p * allergy[p, EGGS] for p in FRIENDS),
        "mold": quicksum(p * allergy[p, MOLD] for p in FRIENDS),
        "nuts": quicksum(p * allergy[p, NUTS] for p in FRIENDS),
        "ragweed": quicksum(p * allergy[p, RAGWEED] for p in FRIENDS),
        "baxter": quicksum(p * surname[p, BAXTER] for p in FRIENDS),
        "lemon": quicksum(p * surname[p, LEMON] for p in FRIENDS),
        "malone": quicksum(p * surname[p, MALONE] for p in FRIENDS),
        "fleet": quicksum(p * surname[p, FLEET] for p in FRIENDS),
    }
    return m, outputs
