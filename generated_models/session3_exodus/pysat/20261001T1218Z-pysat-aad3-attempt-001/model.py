# Exodus: five children each tell a different part of the Exodus story, are of a different age,
# and come from a different country. Using five clues, find which child has which age, country
# and story. Every category is a list of numbers 1..5, and the same number is the same child.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = 5
    pool = IDPool()

    def slots(name):
        # entry i = the number (1..5) of the child that the i-th member of the category belongs to
        return [Integer(f"{name}{i}", 1, n, vpool=pool) for i in range(n)]

    ages = slots("age")  # three, five, seven, eight, ten
    age_value = [3, 5, 7, 8, 10]  # the ages in the order of the list above
    children = slots("child")
    bernice, carl, debby, sammy, ted = children
    countries = slots("country")
    ethiopia, kazakhstan, lithuania, morocco, yemen = countries
    stories = slots("story")
    burning_bush, captivity, moses_youth, passover, ten_commandments = stories

    engine = IntegerEngine(vars=ages + children + countries + stories, vpool=pool)

    # within a category the members belong to different children
    for category in (ages, children, countries, stories):
        engine.add_alldifferent(category)

    # Debby's family is from Lithuania.
    engine.add_equal(debby, lithuania)

    cnf = engine.clausify()

    # same_child[(x, y)] is a literal that is true exactly when x and y are the same child number
    same_child = {}

    def same(x, y):
        if (x, y) not in same_child:
            literal = pool.id(("same", x.name, y.name))
            for number in range(1, n + 1):
                cnf.append([-x.equals(number), -y.equals(number), literal])
                for other in range(1, n + 1):
                    if other != number:
                        cnf.append([-literal, -x.equals(number), -y.equals(other)])
            same_child[(x, y)] = literal
        return same_child[(x, y)]

    def age_gap(first, second, holds):
        """Whenever age i belongs to the child `first` and age j to the child `second`, the two
        ages have to satisfy holds(age i, age j); pairs of ages that do not are ruled out."""
        for i, first_age in enumerate(ages):
            for j, second_age in enumerate(ages):
                if not holds(age_value[i], age_value[j]):
                    cnf.append([-same(first_age, first), -same(second_age, second)])

    # The child who told the story of the Passover is two years older than Bernice.
    age_gap(passover, bernice, lambda a, b: a == b + 2)
    # The child whose family is from Yemen is younger than the child from the Ethiopian family.
    age_gap(yemen, ethiopia, lambda a, b: a < b)
    # The child from the Moroccan family is three years older than Ted.
    age_gap(morocco, ted, lambda a, b: a == b + 3)
    # Sammy is three years older than the child who told the story of Moses's youth.
    age_gap(sammy, moses_youth, lambda a, b: a == b + 3)

    return cnf, {"ages": ages, "children": children, "countries": countries,
                 "stories": stories}
