# Exodus: five children each present a different part of the Exodus story, are of different
# ages, and come from different countries. Match age, child, country and story from five clues.
from hermax.model import Model

# The categories, fixed by the problem. Each entity gets a group number 1..5; entities
# with the same number belong together.
AGE_VALUES = [3, 5, 7, 8, 10]
BERNICE, CARL, DEBBY, SAMMY, TED = range(5)
ETHIOPIA, KAZAKHSTAN, LITHUANIA, MOROCCO, YEMEN = range(5)
BURNING_BUSH, CAPTIVITY, MOSES_YOUTH, PASSOVER, TEN_COMMANDMENTS = range(5)


def forbid_together(m, x, y, a1, a2):
    """Post: x shares a group with age variable a1 and y with a2 only if allowed; called
    for the age pairs that the clue rules out. With one value per variable, x == a1 means
    some group v holds both."""
    for v in range(1, 6):
        for w in range(1, 6):
            m &= (~(x == v) | ~(a1 == v) | ~(y == w) | ~(a2 == w))


def build(instance):
    # The clues are fixed by the problem; the instance carries no data.
    n = 5

    m = Model()
    ages = m.int_vector("ages", n, 1, n)            # three, five, seven, eight, ten
    children = m.int_vector("children", n, 1, n)    # Bernice, Carl, Debby, Sammy, Ted
    countries = m.int_vector("countries", n, 1, n)  # Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen
    stories = m.int_vector("stories", n, 1, n)      # burning bush, captivity, Moses's youth,
    #                                                 Passover, Ten Commandments

    # each category's entities are in different groups
    m &= ages.all_different()
    m &= children.all_different()
    m &= countries.all_different()
    m &= stories.all_different()

    # 1. Debby's family is from Lithuania.
    m &= (children[DEBBY] == countries[LITHUANIA])

    # The remaining clues compare ages: for every pair of ages that breaks the clue, the two
    # entities may not have those ages.
    def clue(x, y, holds):
        for i in range(n):
            for j in range(n):
                if not holds(AGE_VALUES[i], AGE_VALUES[j]):
                    forbid_together(m, x, y, ages[i], ages[j])

    # 2. The child who told the Passover story is two years older than Bernice.
    clue(stories[PASSOVER], children[BERNICE], lambda p, b: p == b + 2)
    # 3. The child from Yemen is younger than the child from Ethiopia.
    clue(countries[YEMEN], countries[ETHIOPIA], lambda y, e: y < e)
    # 4. The child from Morocco is three years older than Ted.
    clue(countries[MOROCCO], children[TED], lambda mo, t: mo == t + 3)
    # 5. Sammy is three years older than the child who told of Moses's youth.
    clue(children[SAMMY], stories[MOSES_YOUTH], lambda s, y: s == y + 3)

    return m, {"ages": ages, "children": children, "countries": countries, "stories": stories}
