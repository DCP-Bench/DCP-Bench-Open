# Allergy puzzle: four friends (Debra=0, Janet=1, Hugh=2, Rick=3) each have one of the
# surnames Baxter, Lemon, Malone, Fleet and one of the allergies eggs, mold, nuts, ragweed.
# Each output gives the friend index (0..3) that has that surname or allergy.
import cvc5.pythonic as cz


def build(instance):
    baxter, lemon, malone, fleet = cz.Ints("baxter lemon malone fleet")
    eggs, mold, nuts, ragweed = cz.Ints("eggs mold nuts ragweed")
    surnames = [baxter, lemon, malone, fleet]
    allergies = [eggs, mold, nuts, ragweed]

    constraints = []
    # Each of them is allergic to something different, and each surname is different.
    for v in surnames + allergies:
        constraints += [v >= 0, v <= 3]
    constraints.append(cz.Distinct(surnames))
    constraints.append(cz.Distinct(allergies))

    # Rick is not allergic to mold.
    constraints.append(mold != 3)

    # Baxter is allergic to eggs.
    constraints.append(baxter == eggs)

    # Hugh is neither surnamed Lemon nor Fleet.
    constraints += [lemon != 2, fleet != 2]

    # Debra is allergic to ragweed.
    constraints.append(ragweed == 0)

    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold.
    constraints += [lemon != 1, eggs != 1, mold != 1]

    outputs = {
        "baxter": baxter,
        "eggs": eggs,
        "fleet": fleet,
        "lemon": lemon,
        "malone": malone,
        "mold": mold,
        "nuts": nuts,
        "ragweed": ragweed,
    }
    return constraints, outputs
