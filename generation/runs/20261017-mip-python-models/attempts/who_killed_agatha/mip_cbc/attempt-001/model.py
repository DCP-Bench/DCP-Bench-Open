# Who killed Agatha? Dreadsbury Mansion puzzle. Three residents: Agatha, the butler and Charles.
# Output: the 0-based index of the killer among the instance's names.
import mip


def _index(names, keyword):
    for i, name in enumerate(names):
        if keyword in name.lower():
            return i
    raise ValueError("no name contains " + keyword)


def build(instance):
    names = instance["names"]
    n = len(names)
    agatha = _index(names, "agatha")
    butler = _index(names, "butler")
    charles = _index(names, "charles")

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    hates = [[model.add_var(f"hates_{i}_{j}", var_type=mip.BINARY) for j in range(n)] for i in range(n)]
    richer = [[model.add_var(f"richer_{i}_{j}", var_type=mip.BINARY) for j in range(n)] for i in range(n)]
    is_killer = [model.add_var(f"is_killer_{i}", var_type=mip.BINARY) for i in range(n)]
    killer = model.add_var("killer", lb=0, ub=n - 1, var_type=mip.INTEGER)

    # Someone in Dreadsbury Mansion killed Aunt Agatha.
    model += mip.xsum(is_killer) == 1
    model += killer == mip.xsum(i * is_killer[i] for i in range(n))

    # A killer always hates, and is no richer than his victim.
    for i in range(n):
        model += hates[i][agatha] >= is_killer[i]
        model += richer[i][agatha] + is_killer[i] <= 1

    # Agatha hates everybody except the butler.
    for j in range(n):
        if j == butler:
            model += hates[agatha][j] == 0
        else:
            model += hates[agatha][j] == 1

    # Charles hates noone that Agatha hates.
    for j in range(n):
        model += hates[charles][j] + hates[agatha][j] <= 1

    # The butler hates everyone not richer than Aunt Agatha.
    for j in range(n):
        model += hates[butler][j] + richer[j][agatha] >= 1

    # The butler hates everyone whom Agatha hates.
    for j in range(n):
        model += hates[butler][j] - hates[agatha][j] >= 0

    # Noone hates everyone.
    for i in range(n):
        model += mip.xsum(hates[i][j] for j in range(n)) <= n - 1

    return model, {"killer": killer}
