# Four friends (Debra=0, Janet=1, Hugh=2, Rick=3) each have a different allergy
# (eggs, mold, nuts, ragweed) and a different surname (Baxter, Lemon, Malone, Fleet).
# Encoding: X[food][p] = 1 when the food is the allergy of friend p;
#           Y[surname][p] = 1 when the surname belongs to friend p.
# Each output is the friend index, sum of p * bool over the friends.
from paramita.modelling import Bool, Iff

FOODS = ["eggs", "mold", "nuts", "ragweed"]
SURNAMES = ["baxter", "lemon", "malone", "fleet"]
FRIENDS = range(4)
DEBRA, JANET, HUGH, RICK = 0, 1, 2, 3


def build(instance):
    X = {f: [Bool(f"allergy_{f}_{p}") for p in FRIENDS] for f in FOODS}
    Y = {s: [Bool(f"surname_{s}_{p}") for p in FRIENDS] for s in SURNAMES}
    cons = []

    # each food is the allergy of exactly one friend
    for f in FOODS:
        cons.append(sum(X[f]) == 1)
    # each friend has exactly one allergy
    for p in FRIENDS:
        cons.append(sum(X[f][p] for f in FOODS) == 1)

    # each surname belongs to exactly one friend
    for s in SURNAMES:
        cons.append(sum(Y[s]) == 1)
    # each friend has exactly one surname
    for p in FRIENDS:
        cons.append(sum(Y[s][p] for s in SURNAMES) == 1)

    # Rick is not allergic to mold
    cons.append(~X["mold"][RICK])

    # Baxter is allergic to eggs
    for p in FRIENDS:
        cons.append(Iff(Y["baxter"][p], X["eggs"][p]))

    # Hugh is neither surnamed Lemon nor Fleet
    cons.append(~Y["lemon"][HUGH])
    cons.append(~Y["fleet"][HUGH])

    # Debra is allergic to ragweed
    cons.append(X["ragweed"][DEBRA])

    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold
    cons.append(~Y["lemon"][JANET])
    cons.append(~X["eggs"][JANET])
    cons.append(~X["mold"][JANET])

    outputs = {}
    for f in FOODS:
        outputs[f] = sum(p * X[f][p] for p in FRIENDS)
    for s in SURNAMES:
        outputs[s] = sum(p * Y[s][p] for p in FRIENDS)
    return cons, outputs
