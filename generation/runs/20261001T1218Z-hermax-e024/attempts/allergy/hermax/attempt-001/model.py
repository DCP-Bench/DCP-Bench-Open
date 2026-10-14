# Allergy: four friends, Debra, Janet, Hugh and Rick, are each allergic to something
# different (eggs, mold, nuts or ragweed) and each has a different surname (Baxter, Lemon,
# Malone or Fleet). From the clues, match every allergy and every surname with a friend.
from hermax.model import Model


def build(instance):
    # This puzzle has no instance data: the four friends and the clues are part of the
    # problem itself, so they are written here as constants. The friends are numbered
    # Debra = 0, Janet = 1, Hugh = 2, Rick = 3, as in the statement.
    Debra, Janet, Hugh, Rick = 0, 1, 2, 3
    n = 4

    m = Model()
    # foods[i] = the friend allergic to the i-th allergen (eggs, mold, nuts, ragweed)
    foods = m.int_vector("foods", n, 0, n - 1)
    eggs, mold, nuts, ragweed = (foods[i] for i in range(n))
    # surnames[i] = the friend with the i-th surname (Baxter, Lemon, Malone, Fleet)
    surnames = m.int_vector("surnames", n, 0, n - 1)
    baxter, lemon, malone, fleet = (surnames[i] for i in range(n))

    # everyone is allergic to something different and has a different surname
    m &= foods.all_different()
    m &= surnames.all_different()

    # Rick is not allergic to mold
    m &= (mold != Rick)
    # Baxter is allergic to eggs: the friend allergic to eggs is the one called Baxter
    m &= (eggs == baxter)
    # Hugh is neither surnamed Lemon nor Fleet
    m &= (lemon != Hugh)
    m &= (fleet != Hugh)
    # Debra is allergic to ragweed
    m &= (ragweed == Debra)
    # Janet is not Lemon, and is allergic neither to eggs nor to mold
    m &= (lemon != Janet)
    m &= (eggs != Janet)
    m &= (mold != Janet)

    return m, {"eggs": eggs, "mold": mold, "nuts": nuts, "ragweed": ragweed,
               "baxter": baxter, "lemon": lemon, "malone": malone, "fleet": fleet}
