"""Exodus: match five children to an age, a country of origin and a part of the Exodus story."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data. Each category's items are placed on the
# slots 1..5; items sharing a slot belong to the same child.
AGES = [3, 5, 7, 8, 10]
CATEGORIES = {
    "ages": ["age3", "age5", "age7", "age8", "age10"],
    "children": ["bernice", "carl", "debby", "sammy", "ted"],
    "countries": ["ethiopia", "kazakhstan", "lithuania", "morocco", "yemen"],
    "stories": ["burning_bush", "captivity", "moses_youth", "passover", "ten_commandments"],
}
SLOTS = range(1, 6)
# Ages differ by at most 7, so 10 relaxes any age difference constraint below.
BIG_M = 10


def build(instance):
    model = gp.Model("session3_exodus")

    # at[item, s] = 1 when the item is on slot s. Within a category the five
    # items take the five slots, one each.
    at = {}
    for items in CATEGORIES.values():
        for item in items:
            for s in SLOTS:
                at[item, s] = model.addVar(vtype=GRB.BINARY, name=f"at[{item},{s}]")
            model.addConstr(gp.quicksum(at[item, s] for s in SLOTS) == 1, name=f"placed[{item}]")
        for s in SLOTS:
            model.addConstr(gp.quicksum(at[item, s] for item in items) == 1, name=f"different[{items[0]},{s}]")

    # The age of the child on slot s.
    age = {s: gp.quicksum(AGES[k] * at[item, s] for k, item in enumerate(CATEGORIES["ages"])) for s in SLOTS}

    def older_by(older, younger, gap, name):
        """If `older` is on slot s1 and `younger` on slot s2, then
        age(s1) == age(s2) + gap; relaxed by BIG_M unless both hold."""
        for s1 in SLOTS:
            for s2 in SLOTS:
                off = 2 - at[older, s1] - at[younger, s2]
                model.addConstr(age[s1] - age[s2] - gap <= BIG_M * off, name=f"{name}_upper[{s1},{s2}]")
                model.addConstr(age[s1] - age[s2] - gap >= -BIG_M * off, name=f"{name}_lower[{s1},{s2}]")

    # 1. Debby's family is from Lithuania.
    for s in SLOTS:
        model.addConstr(at["debby", s] == at["lithuania", s], name=f"clue1[{s}]")

    # 2. The child who told the Passover story is two years older than Bernice.
    older_by("passover", "bernice", 2, "clue2")

    # 3. The child from Yemen is younger than the child from Ethiopia.
    for s1 in SLOTS:
        for s2 in SLOTS:
            off = 2 - at["yemen", s1] - at["ethiopia", s2]
            model.addConstr(age[s1] <= age[s2] - 1 + BIG_M * off, name=f"clue3[{s1},{s2}]")

    # 4. The child from Morocco is three years older than Ted.
    older_by("morocco", "ted", 3, "clue4")

    # 5. Sammy is three years older than the child who told of Moses's youth.
    older_by("sammy", "moses_youth", 3, "clue5")

    def slots_of(items):
        return [gp.quicksum(s * at[item, s] for s in SLOTS) for item in items]

    return model, {name: slots_of(items) for name, items in CATEGORIES.items()}
