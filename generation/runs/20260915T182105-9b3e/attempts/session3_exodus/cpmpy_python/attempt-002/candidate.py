import cpmpy as cp


def build(instance):
    """Exodus: match five children to an age, a country of origin and a part of
    the story.

    The puzzle states its own five children, ages, countries and stories, so
    `instance` is unused.  Every variable holds a group number 1..5, and two
    variables sharing a number means they describe the same child.
    """
    del instance

    ages = cp.intvar(1, 5, shape=5, name="ages")
    children = cp.intvar(1, 5, shape=5, name="children")
    countries = cp.intvar(1, 5, shape=5, name="countries")
    stories = cp.intvar(1, 5, shape=5, name="stories")

    bernice, carl, debby, sammy, ted = children
    ethiopia, kazakhstan, lithuania, morocco, yemen = countries
    burning_bush, captivity, moses_youth, passover, ten_commandments = stories

    # The age slots stand for these actual ages, in order.
    age_values = [3, 5, 7, 8, 10]

    def forbidden_pairings(older, younger, holds):
        """Rule out every pairing of age slots the arithmetic forbids.

        `older` and `younger` each name a child; for each pair of age slots
        that could be theirs, `holds` says whether those two ages are
        compatible with the clue.  Where they are not, the pairing is
        forbidden outright.
        """
        return [
            ~((ages[i] == older) & (ages[j] == younger))
            for i in range(5)
            for j in range(5)
            if not holds(age_values[i], age_values[j])
        ]

    constraints = [
        cp.AllDifferent(ages),
        cp.AllDifferent(children),
        cp.AllDifferent(countries),
        cp.AllDifferent(stories),
        # 1. Debby's family is from Lithuania.
        debby == lithuania,
    ]
    # 2. The Passover child is two years older than Bernice.
    constraints += forbidden_pairings(passover, bernice, lambda a, b: a == b + 2)
    # 3. The Yemeni child is younger than the Ethiopian child.
    constraints += forbidden_pairings(yemen, ethiopia, lambda a, b: a < b)
    # 4. The Moroccan child is three years older than Ted.
    constraints += forbidden_pairings(morocco, ted, lambda a, b: a == b + 3)
    # 5. Sammy is three years older than the child who told of Moses's youth.
    constraints += forbidden_pairings(sammy, moses_youth, lambda a, b: a == b + 3)

    return cp.Model(constraints), {
        "ages": ages,
        "children": children,
        "countries": countries,
        "stories": stories,
    }
