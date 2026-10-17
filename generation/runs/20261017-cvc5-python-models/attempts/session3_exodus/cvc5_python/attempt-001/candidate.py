# Session 3 Exodus: five children, ages, countries of origin and Exodus story parts.
# Each list is indexed by attribute value; its entries give the shared row id (1..5)
# of the entity that has that value. Two entities share a row exactly when their ids are equal.
import cvc5.pythonic as cz

AGES = [3, 5, 7, 8, 10]
# Index order: ages[0] = 3, children[0] = Bernice, countries[0] = Ethiopia, stories[0] = burning bush.
BERNICE, CARL, DEBBY, SAMMY, TED = 0, 1, 2, 3, 4
ETHIOPIA, KAZAKHSTAN, LITHUANIA, MOROCCO, YEMEN = 0, 1, 2, 3, 4
BURNING_BUSH, CAPTIVITY, MOSES_YOUTH, PASSOVER, TEN_COMMANDMENTS = 0, 1, 2, 3, 4


def build(instance):
    ages = cz.Ints("ages_0 ages_1 ages_2 ages_3 ages_4")
    children = cz.Ints("children_0 children_1 children_2 children_3 children_4")
    countries = cz.Ints("countries_0 countries_1 countries_2 countries_3 countries_4")
    stories = cz.Ints("stories_0 stories_1 stories_2 stories_3 stories_4")

    constraints = []

    # Each list is a permutation of 1..5, so every row holds one entity of each category.
    for lst in (ages, children, countries, stories):
        constraints += [v >= 1 for v in lst]
        constraints += [v <= 5 for v in lst]
        constraints.append(cz.Distinct(list(lst)))

    def age_of(row):
        # Age value of the row whose age entry carries the id `row`.
        return cz.Sum([cz.If(ages[a] == row, AGES[a], 0) for a in range(5)])

    # Debby's family is from Lithuania.
    # Debby's family is from Lithuania.
    constraints.append(countries[LITHUANIA] == children[DEBBY])
    # The child who told the story of the Passover is two years older than Bernice.
    constraints.append(age_of(stories[PASSOVER]) == age_of(children[BERNICE]) + 2)
    # The child whose family is from Yemen is younger than the child from the Ethiopian family.
    constraints.append(age_of(countries[YEMEN]) < age_of(countries[ETHIOPIA]))
    # The child from the Moroccan family is three years older than Ted.
    constraints.append(age_of(countries[MOROCCO]) == age_of(children[TED]) + 3)
    # Sammy is three years older than the child who told the story of Moses's youth in the house of the Pharaoh.
    constraints.append(age_of(children[SAMMY]) == age_of(stories[MOSES_YOUTH]) + 3)

    outputs = {
        "ages": ages,
        "children": children,
        "countries": countries,
        "stories": stories,
    }
    return constraints, outputs
