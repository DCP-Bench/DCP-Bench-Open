# Allergy puzzle: four friends (Debra=0, Janet=1, Hugh=2, Rick=3) each have one
# allergy (eggs, mold, nuts, ragweed) and one surname (Baxter, Lemon, Malone, Fleet).
# Output: for each allergy and each surname, the friend index who has it.
import mip

FRIENDS = range(4)
DEBRA, JANET, HUGH, RICK = 0, 1, 2, 3
ALLERGIES = ["eggs", "mold", "nuts", "ragweed"]
SURNAMES = ["baxter", "lemon", "malone", "fleet"]


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # A[f][k] = 1 when friend f is allergic to allergy k
    A = {(f, k): model.add_var(f"A_{f}_{k}", var_type=mip.BINARY)
         for f in FRIENDS for k in ALLERGIES}
    # S[f][s] = 1 when friend f has surname s
    S = {(f, s): model.add_var(f"S_{f}_{s}", var_type=mip.BINARY)
         for f in FRIENDS for s in SURNAMES}

    # Each friend has exactly one allergy and exactly one surname.
    for f in FRIENDS:
        model.add_constr(mip.xsum(A[f, k] for k in ALLERGIES) == 1)
        model.add_constr(mip.xsum(S[f, s] for s in SURNAMES) == 1)

    # Each allergy and each surname belongs to exactly one friend.
    for k in ALLERGIES:
        model.add_constr(mip.xsum(A[f, k] for f in FRIENDS) == 1)
    for s in SURNAMES:
        model.add_constr(mip.xsum(S[f, s] for f in FRIENDS) == 1)

    # Output variables: the friend index holding each allergy or surname.
    out = {}
    for k in ALLERGIES:
        out[k] = model.add_var(f"allergy_{k}", lb=0, ub=3, var_type=mip.INTEGER)
        model.add_constr(out[k] == mip.xsum(f * A[f, k] for f in FRIENDS))
    for s in SURNAMES:
        out[s] = model.add_var(f"surname_{s}", lb=0, ub=3, var_type=mip.INTEGER)
        model.add_constr(out[s] == mip.xsum(f * S[f, s] for f in FRIENDS))

    # Rick is not allergic to mold.
    model.add_constr(A[RICK, "mold"] == 0)

    # Baxter is allergic to eggs.
    model.add_constr(out["baxter"] == out["eggs"])

    # Hugh is neither surnamed Lemon nor Fleet.
    model.add_constr(S[HUGH, "lemon"] == 0)
    model.add_constr(S[HUGH, "fleet"] == 0)

    # Debra is allergic to ragweed.
    model.add_constr(A[DEBRA, "ragweed"] == 1)

    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold.
    model.add_constr(S[JANET, "lemon"] == 0)
    model.add_constr(A[JANET, "eggs"] == 0)
    model.add_constr(A[JANET, "mold"] == 0)

    outputs = {
        "eggs": out["eggs"],
        "mold": out["mold"],
        "nuts": out["nuts"],
        "ragweed": out["ragweed"],
        "baxter": out["baxter"],
        "lemon": out["lemon"],
        "malone": out["malone"],
        "fleet": out["fleet"],
    }
    return model, outputs
