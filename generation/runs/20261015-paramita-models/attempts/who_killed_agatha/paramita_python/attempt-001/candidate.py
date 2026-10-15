# Who killed Aunt Agatha? Three people live in Dreadsbury Mansion: Agatha
# herself, the butler and Charles. The names come from the instance, in that
# order (index 0 is Agatha, index 1 is the butler, index 2 is Charles).
#
# hates[x][y] means x hates y; richer[x][y] means x is richer than y.

from paramita.modelling import Bool, If

AGATHA, BUTLER, CHARLES = 0, 1, 2


def build(instance):
    names = instance["names"]
    n = len(names)

    hates = [[Bool(f"hates_{x}_{y}") for y in range(n)] for x in range(n)]
    richer = [[Bool(f"richer_{x}_{y}") for y in range(n)] for x in range(n)]
    killer = [Bool(f"killer_{x}") for x in range(n)]

    cons = []

    # richer is a strict order: nobody is richer than himself, and of two
    # people at most one is richer than the other, and richer is transitive
    cons += [~richer[x][x] for x in range(n)]
    cons += [If(richer[x][y], ~richer[y][x]) for x in range(n) for y in range(n)]
    cons += [If(richer[x][y] & richer[y][z], richer[x][z])
             for x in range(n) for y in range(n) for z in range(n)]

    # exactly one of the three people killed Agatha
    cons.append(sum(killer) == 1)

    # a killer always hates his victim, and is no richer than his victim
    # (the victim is Agatha)
    cons += [If(killer[x], hates[x][AGATHA]) for x in range(n)]
    cons += [If(killer[x], ~richer[x][AGATHA]) for x in range(n)]

    # Charles hates noone that Agatha hates
    cons += [If(hates[AGATHA][y], ~hates[CHARLES][y]) for y in range(n)]

    # Agatha hates everybody except the butler
    cons += [~hates[AGATHA][y] if y == BUTLER else hates[AGATHA][y] for y in range(n)]

    # the butler hates everyone not richer than Aunt Agatha
    cons += [If(~richer[y][AGATHA], hates[BUTLER][y]) for y in range(n)]

    # the butler hates everyone whom Agatha hates
    cons += [If(hates[AGATHA][y], hates[BUTLER][y]) for y in range(n)]

    # noone hates everyone: every person hates at least one other person not hated
    cons += [sum(~hates[x][y] for y in range(n)) >= 1 for x in range(n)]

    # output: the 0-based index of the killer
    killer_index = sum(x * killer[x] for x in range(n))
    return cons, {"killer": killer_index}
