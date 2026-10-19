# Harriet's four shoe purchases (ecru espadrilles, fuchsia flats, purple pumps,
# suede sandals) and the four stores (Foot Farm, Heels in a Handcart, The Shoe
# Palace, Tootsies). Each shoe and each store gets its own stop number 1..4,
# and the stop numbers within each group are all different.
import mip


def add_stop(model, name, n, ch_list):
    # each item gets one stop number in 1..n, given by one-hot binaries
    x = model.add_var(name, lb=1, ub=n, var_type=mip.INTEGER)
    ch = [model.add_var(f"{name}_at_{v}", var_type=mip.BINARY) for v in range(1, n + 1)]
    model.add_constr(mip.xsum(ch) == 1, name=f"{name}_one")
    model.add_constr(
        x == mip.xsum(v * c for v, c in zip(range(1, n + 1), ch)),
        name=f"{name}_value",
    )
    ch_list.append(ch)
    return x, ch


def build(instance):
    n = 4
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    shoe_ch = []
    ecru, ecru_ch = add_stop(model, "ecruespadrilles", n, shoe_ch)
    fuchsia, fuchsia_ch = add_stop(model, "fuchsiaflats", n, shoe_ch)
    purple, purple_ch = add_stop(model, "purplepumps", n, shoe_ch)
    suede, suede_ch = add_stop(model, "suedesandals", n, shoe_ch)

    store_ch = []
    footfarm, footfarm_ch = add_stop(model, "footfarm", n, store_ch)
    heels, heels_ch = add_stop(model, "heelsinahandcart", n, store_ch)
    shoepalace, shoepalace_ch = add_stop(model, "theshoepalace", n, store_ch)
    tootsies, tootsies_ch = add_stop(model, "tootsies", n, store_ch)

    # the shoes are bought at different stops: each stop number is used once
    for v in range(n):
        model += mip.xsum(ch[v] for ch in shoe_ch) == 1
    # the stores are visited at different stops: each stop number is used once
    for v in range(n):
        model += mip.xsum(ch[v] for ch in store_ch) == 1

    # Harriet bought fuchsia flats at Heels in a Handcart.
    model += fuchsia - heels == 0

    # The store she visited just after buying her purple pumps was not Tootsies.
    # Forbid purple pumps at stop k together with Tootsies at stop k+1.
    for k in range(n - 1):
        model += purple_ch[k] + tootsies_ch[k + 1] <= 1

    # The Foot Farm was Harriet's second stop.
    model += footfarm == 2

    # Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    model += suede - shoepalace == 2

    return model, {
        "ecruespadrilles": ecru,
        "fuchsiaflats": fuchsia,
        "purplepumps": purple,
        "suedesandals": suede,
        "footfarm": footfarm,
        "heelsinahandcart": heels,
        "theshoepalace": shoepalace,
        "tootsies": tootsies,
    }
