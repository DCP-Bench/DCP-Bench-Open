"""Exodus: five children of different ages, from five different countries, each told a
different part of the Exodus story. Match ages, children, countries and stories from five
clues.

Every item gets a slot 1..5; items with the same slot belong together.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data; the items and ages are from the statement.
    slots = range(1, 6)
    ages = {"age3": 3, "age5": 5, "age7": 7, "age8": 8, "age10": 10}
    groups = {
        "ages": list(ages),
        "children": ["bernice", "carl", "debby", "sammy", "ted"],
        "countries": ["ethiopia", "kazakhstan", "lithuania", "morocco", "yemen"],
        "stories": ["burning_bush", "captivity", "moses_youth", "passover", "ten_commandments"],
    }

    model = Model("exodus")

    # at[e, s] is 1 when item e has slot s. Within a group every item has one slot and no
    # two items share one (all different).
    at = {}
    for items in groups.values():
        for e in items:
            for s in slots:
                at[e, s] = model.binary_var(name=f"{e}_at_{s}")
            model.add_constraint(model.sum(at[e, s] for s in slots) == 1)
        for s in slots:
            model.add_constraint(model.sum(at[e, s] for e in items) == 1)

    # The age of item e: has_age[e, a] is 1 when e shares its slot with age a. If e and a
    # are both at slot s, has_age[e, a] is forced to 1; exactly one age is chosen, so it is
    # the age at e's slot.
    def age_of(e):
        has_age = {a: model.binary_var(name=f"{e}_has_{a}") for a in ages}
        for a in ages:
            for s in slots:
                model.add_constraint(has_age[a] >= at[e, s] + at[a, s] - 1)
        model.add_constraint(model.sum(has_age.values()) == 1)
        return model.sum(ages[a] * has_age[a] for a in ages)

    # 1. Debby's family is from Lithuania.
    for s in slots:
        model.add_constraint(at["debby", s] == at["lithuania", s])
    # 2. The child who told the Passover story is two years older than Bernice.
    model.add_constraint(age_of("passover") == age_of("bernice") + 2)
    # 3. The child from Yemen is younger than the child from Ethiopia.
    model.add_constraint(age_of("yemen") <= age_of("ethiopia") - 1)
    # 4. The child from Morocco is three years older than Ted.
    model.add_constraint(age_of("morocco") == age_of("ted") + 3)
    # 5. Sammy is three years older than the child who told of Moses's youth.
    model.add_constraint(age_of("sammy") == age_of("moses_youth") + 3)

    # Each output lists the slot of every item of a group, in the statement's order.
    outputs = {name: [model.sum(s * at[e, s] for s in slots) for e in items]
               for name, items in groups.items()}
    return model, outputs
