# Exodus: five children each tell a different part of the Exodus story, have a
# different age and come from a different country. From five clues, find the
# age, country and story of each child.
import z3


def build(instance):
    del instance  # the puzzle states its own children and clues

    # Problem data: the five ages, in the order three, five, seven, eight, ten.
    age_values = [3, 5, 7, 8, 10]

    # The four categories are each a permutation of the labels 1..5; the same label
    # in two categories means the same child. ages[k] is the label of the child of
    # age age_values[k], and so on for the other categories in statement order.
    ages = z3.IntVector("ages", 5)
    children = z3.IntVector("children", 5)
    countries = z3.IntVector("countries", 5)
    stories = z3.IntVector("stories", 5)
    bernice, carl, debby, sammy, ted = children
    ethiopia, kazakhstan, lithuania, morocco, yemen = countries
    burning_bush, captivity, moses_youth, passover, ten_commandments = stories

    solver = z3.Solver()
    for v in list(ages) + list(children) + list(countries) + list(stories):
        solver.add(v >= 1, v <= 5)

    # Within each category all five entries are different.
    for category in (ages, children, countries, stories):
        solver.add(z3.Distinct(category))

    def age_of(label):
        # Age in years of the child carrying `label`. The labels in `ages` are a
        # permutation, so exactly one entry matches. Z3 has no Element constraint,
        # so the lookup is an If chain.
        expr = z3.IntVal(age_values[-1])
        for k in reversed(range(len(age_values) - 1)):
            expr = z3.If(ages[k] == label, age_values[k], expr)
        return expr

    # 1. Debby's family is from Lithuania.
    solver.add(debby == lithuania)

    # 2. The child who told the story of the Passover is two years older than Bernice.
    solver.add(age_of(passover) == age_of(bernice) + 2)

    # 3. The child whose family is from Yemen is younger than the child from the
    #    Ethiopian family.
    solver.add(age_of(yemen) < age_of(ethiopia))

    # 4. The child from the Moroccan family is three years older than Ted.
    solver.add(age_of(morocco) == age_of(ted) + 3)

    # 5. Sammy is three years older than the child who told the story of Moses's
    #    youth in the house of the Pharaoh.
    solver.add(age_of(sammy) == age_of(moses_youth) + 3)

    return solver, {"ages": list(ages), "children": list(children),
                    "countries": list(countries), "stories": list(stories)}
