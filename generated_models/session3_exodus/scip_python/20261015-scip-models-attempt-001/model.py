# Exodus story puzzle: match each of five children with an age, a family's country of origin and a part of the Exodus story.
from pyscipopt import Model, quicksum

# Problem constants from the statement (the instance carries no fields).
CHILDREN = ["Bernice", "Carl", "Debby", "Sammy", "Ted"]  # child numbers 1..5 in this order
AGES = [3, 5, 7, 8, 10]
COUNTRIES = ["Ethiopia", "Kazakhstan", "Lithuania", "Morocco", "Yemen"]
STORIES = ["burning bush", "captivity", "Moses's youth", "Passover", "Ten Commandments"]
BERNICE, DEBBY, SAMMY, TED = 0, 2, 3, 4
ETHIOPIA, LITHUANIA, MOROCCO, YEMEN = 0, 2, 3, 4
MOSES, PASSOVER = 2, 3


def build(instance):
    n = len(CHILDREN)
    m = Model("session3_exodus")

    # age[e, a] = 1 if child e is AGES[a] years old
    age = {(e, a): m.addVar(name=f"age_{e}_{a}", vtype="B") for e in range(n) for a in range(n)}
    # country[e, c] = 1 if child e's family is from COUNTRIES[c]
    country = {(e, c): m.addVar(name=f"country_{e}_{c}", vtype="B") for e in range(n) for c in range(n)}
    # story[e, s] = 1 if child e told STORIES[s]
    story = {(e, s): m.addVar(name=f"story_{e}_{s}", vtype="B") for e in range(n) for s in range(n)}

    def age_of(e):
        return quicksum(AGES[a] * age[e, a] for a in range(n))

    def eq_if(b, lhs, rhs):
        # lhs == rhs holds whenever binary b is 1
        m.addConsIndicator(lhs <= rhs, binvar=b)
        m.addConsIndicator(lhs >= rhs, binvar=b)

    # each child has exactly one age, country and story; each value is used by exactly one child
    for e in range(n):
        m.addCons(quicksum(age[e, a] for a in range(n)) == 1)
        m.addCons(quicksum(country[e, c] for c in range(n)) == 1)
        m.addCons(quicksum(story[e, s] for s in range(n)) == 1)
    for k in range(n):
        m.addCons(quicksum(age[e, k] for e in range(n)) == 1)
        m.addCons(quicksum(country[e, k] for e in range(n)) == 1)
        m.addCons(quicksum(story[e, k] for e in range(n)) == 1)

    # 1. Debby's family is from Lithuania.
    m.addCons(country[DEBBY, LITHUANIA] == 1)

    # 2. The child who told the story of the Passover is two years older than Bernice.
    for e in range(n):
        eq_if(story[e, PASSOVER], age_of(e), age_of(BERNICE) + 2)

    # 3. The child whose family is from Yemen is younger than the child from the Ethiopian family.
    for e in range(n):
        for f in range(n):
            if e == f:
                continue
            both = m.addVar(name=f"yemen_{e}_ethiopia_{f}", vtype="B")
            m.addConsAnd([country[e, YEMEN], country[f, ETHIOPIA]], both)
            m.addConsIndicator(age_of(e) <= age_of(f) - 1, binvar=both)

    # 4. The child from the Moroccan family is three years older than Ted.
    for e in range(n):
        eq_if(country[e, MOROCCO], age_of(e), age_of(TED) + 3)

    # 5. Sammy is three years older than the child who told the story of Moses's youth in the house of the Pharaoh.
    for e in range(n):
        eq_if(story[e, MOSES], age_of(SAMMY), age_of(e) + 3)

    # Outputs: each list slot is a value of its category; the entry is the number (child index + 1) of the child with that value.
    ages = [quicksum((e + 1) * age[e, a] for e in range(n)) for a in range(n)]
    countries = [quicksum((e + 1) * country[e, c] for e in range(n)) for c in range(n)]
    stories = [quicksum((e + 1) * story[e, s] for e in range(n)) for s in range(n)]
    # the child numbering is fixed by the order of the names in the statement
    children = []
    for e in range(n):
        v = m.addVar(name=f"child_{e}", vtype="I", lb=e + 1, ub=e + 1)
        children.append(v)

    return m, {"ages": ages, "children": children, "countries": countries, "stories": stories}
