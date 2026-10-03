"""Exodus: five children (Bernice, Carl, Debby, Sammy, Ted) of different ages (3, 5, 7, 8,
10), whose families come from different countries (Ethiopia, Kazakhstan, Lithuania,
Morocco, Yemen), each tell a different part of the Exodus story (burning bush, captivity,
Moses's youth, Passover, Ten Commandments). Find who is who from the clues.

The model reports, for each age, child, country and story, a slot number 1..5; entries with
the same slot belong to the same child.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    slots = range(1, 6)
    categories = {
        "ages": ["age3", "age5", "age7", "age8", "age10"],
        "children": ["bernice", "carl", "debby", "sammy", "ted"],
        "countries": ["ethiopia", "kazakhstan", "lithuania", "morocco", "yemen"],
        "stories": ["burning_bush", "captivity", "moses_youth", "passover", "ten_commandments"],
    }
    age_value = {"age3": 3, "age5": 5, "age7": 7, "age8": 8, "age10": 10}

    problem = pulp.LpProblem("exodus", pulp.LpMinimize)  # satisfaction

    # in_slot[e][s] = 1 if entity e has slot s; within a category all slots differ
    in_slot = {e: {s: pulp.LpVariable(f"slot_{e}_{s}", cat="Binary") for s in slots}
               for items in categories.values() for e in items}
    for items in categories.values():
        for e in items:
            problem += pulp.lpSum(in_slot[e].values()) == 1
        for s in slots:
            problem += pulp.lpSum(in_slot[e][s] for e in items) == 1

    # same_age[e][a] = 1 if entity e shares its slot with age a, so that the age of e is
    # linear in these binaries. Sharing a slot forces it to 1, and exactly one is 1.
    def age_of(e):
        same_age = {a: pulp.LpVariable(f"age_{e}_{a}", cat="Binary") for a in categories["ages"]}
        for a, var in same_age.items():
            for s in slots:
                problem.addConstraint(var >= in_slot[e][s] + in_slot[a][s] - 1)
        problem.addConstraint(pulp.lpSum(same_age.values()) == 1)
        return pulp.lpSum(age_value[a] * var for a, var in same_age.items())

    # 1. Debby's family is from Lithuania.
    for s in slots:
        problem += in_slot["debby"][s] == in_slot["lithuania"][s]
    # 2. The child who told the story of the Passover is two years older than Bernice.
    problem += age_of("passover") == age_of("bernice") + 2
    # 3. The child from Yemen is younger than the child from the Ethiopian family.
    problem += age_of("yemen") + 1 <= age_of("ethiopia")
    # 4. The child from the Moroccan family is three years older than Ted.
    problem += age_of("morocco") == age_of("ted") + 3
    # 5. Sammy is three years older than the child who told of Moses's youth.
    problem += age_of("sammy") == age_of("moses_youth") + 3

    return problem, {key: [pulp.lpSum(s * var for s, var in in_slot[e].items()) for e in items]
                     for key, items in categories.items()}
