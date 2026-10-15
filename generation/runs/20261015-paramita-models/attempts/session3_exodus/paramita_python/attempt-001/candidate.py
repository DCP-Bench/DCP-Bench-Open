# Exodus association puzzle: five children (Bernice, Carl, Debby, Sammy, Ted)
# each have an age, a family country and the part of the Exodus story they
# related. Every child is one row of the association; the row number is the
# child's position in the problem statement (Bernice = 1 ... Ted = 5).
# Encoding: one-hot Booleans per child for age, country and story. The integer
# age of a child is the sum of its years times its one-hot age Booleans.
# The outputs ages/countries/stories are indexed by value and hold the number
# of the child that has that value. The problem data (value lists, child
# names) is fixed by the problem statement, so it is written here.
from paramita.modelling import Bool, If

# Problem constants (fixed by the problem statement, not by the instance).
CHILDREN = ["Bernice", "Carl", "Debby", "Sammy", "Ted"]
AGES = [3, 5, 7, 8, 10]                      # ages[j] is AGES[j] years
COUNTRIES = ["Ethiopia", "Kazakhstan", "Lithuania", "Morocco", "Yemen"]
STORIES = ["burning bush", "captivity", "Moses's youth", "Passover", "Ten Commandments"]

BERNICE, CARL, DEBBY, SAMMY, TED = range(5)
ETHIOPIA, KAZAKHSTAN, LITHUANIA, MOROCCO, YEMEN = range(5)
BURNING_BUSH, CAPTIVITY, MOSES_YOUTH, PASSOVER, TEN_COMMANDMENTS = range(5)


def build(instance):
    n = len(CHILDREN)
    cons = []

    # One-hot Booleans: age[c][v], country[c][v], story[c][v].
    age = [[Bool(f"age_{c}_{v}") for v in range(n)] for c in range(n)]
    country = [[Bool(f"country_{c}_{v}") for v in range(n)] for c in range(n)]
    story = [[Bool(f"story_{c}_{v}") for v in range(n)] for c in range(n)]

    # Each child has exactly one age, one family country and one story.
    for c in range(n):
        cons.append(sum(age[c]) == 1)
        cons.append(sum(country[c]) == 1)
        cons.append(sum(story[c]) == 1)

    # Each age, each country and each story belongs to exactly one child.
    for v in range(n):
        cons.append(sum(age[c][v] for c in range(n)) == 1)
        cons.append(sum(country[c][v] for c in range(n)) == 1)
        cons.append(sum(story[c][v] for c in range(n)) == 1)

    # The integer age of each child, in years.
    years = [sum(AGES[v] * age[c][v] for v in range(n)) for c in range(n)]

    # Clue 1: Debby's family is from Lithuania.
    cons.append(country[DEBBY][LITHUANIA])

    # Clue 2: the child who told the story of the Passover is two years older
    # than Bernice.
    for c in range(n):
        cons.append(If(story[c][PASSOVER], years[c] == years[BERNICE] + 2))

    # Clue 3: the child whose family is from Yemen is younger than the child
    # from the Ethiopian family.
    for c in range(n):
        for d in range(n):
            if c != d:
                cons.append(If(country[c][YEMEN] & country[d][ETHIOPIA], years[c] < years[d]))

    # Clue 4: the child from the Moroccan family is three years older than Ted.
    for c in range(n):
        cons.append(If(country[c][MOROCCO], years[c] == years[TED] + 3))

    # Clue 5: Sammy is three years older than the child who told the story of
    # Moses's youth in the house of the Pharaoh.
    for c in range(n):
        cons.append(If(story[c][MOSES_YOUTH], years[SAMMY] == years[c] + 3))

    # Output: the child number (row) that holds each value. Child c has
    # number c + 1, so the number is the weighted sum of its one-hot Booleans.
    ages_out = [sum((c + 1) * age[c][v] for c in range(n)) for v in range(n)]
    countries_out = [sum((c + 1) * country[c][v] for c in range(n)) for v in range(n)]
    stories_out = [sum((c + 1) * story[c][v] for c in range(n)) for v in range(n)]
    children_out = [c + 1 for c in range(n)]

    outputs = {
        "ages": ages_out,
        "children": children_out,
        "countries": countries_out,
        "stories": stories_out,
    }
    return cons, outputs
