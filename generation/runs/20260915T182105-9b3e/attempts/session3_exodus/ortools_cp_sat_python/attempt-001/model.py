from ortools.sat.python import cp_model


def build(instance):
    """Exodus: match five children to an age, a country of origin and a part of
    the story.

    The puzzle states its own five children, ages, countries and stories, so
    `instance` is unused.  Every variable holds a group number 1..5, and two
    variables sharing a number means they describe the same child.
    """
    del instance

    model = cp_model.CpModel()
    ages = [model.new_int_var(1, 5, f"age{i}") for i in range(5)]
    children = [model.new_int_var(1, 5, f"child{i}") for i in range(5)]
    countries = [model.new_int_var(1, 5, f"country{i}") for i in range(5)]
    stories = [model.new_int_var(1, 5, f"story{i}") for i in range(5)]

    bernice, carl, debby, sammy, ted = children
    ethiopia, kazakhstan, lithuania, morocco, yemen = countries
    burning_bush, captivity, moses_youth, passover, ten_commandments = stories

    # The age slots stand for these actual ages, in order.
    age_values = [3, 5, 7, 8, 10]

    model.add_all_different(ages)
    model.add_all_different(children)
    model.add_all_different(countries)
    model.add_all_different(stories)

    # 1. Debby's family is from Lithuania.
    model.add(debby == lithuania)

    def matches(variable, target, name):
        """A Boolean that is true exactly when the two variables agree."""
        same = model.new_bool_var(name)
        model.add(variable == target).only_enforce_if(same)
        model.add(variable != target).only_enforce_if(~same)
        return same

    def relate(older, younger, holds, label):
        """Rule out every pairing of age slots the arithmetic forbids.

        `older` and `younger` each name a child; for each pair of age slots
        that could be theirs, `holds` says whether those two ages are
        compatible with the clue.  Where they are not, the pairing is
        forbidden outright.
        """
        for i in range(5):
            for j in range(5):
                if holds(age_values[i], age_values[j]):
                    continue
                first = matches(ages[i], older, f"{label}_{i}_{j}_a")
                second = matches(ages[j], younger, f"{label}_{i}_{j}_b")
                model.add_bool_or([~first, ~second])

    # 2. The Passover child is two years older than Bernice.
    relate(passover, bernice, lambda a, b: a == b + 2, "passover")
    # 3. The Yemeni child is younger than the Ethiopian child.
    relate(yemen, ethiopia, lambda a, b: a < b, "yemen")
    # 4. The Moroccan child is three years older than Ted.
    relate(morocco, ted, lambda a, b: a == b + 3, "morocco")
    # 5. Sammy is three years older than the child who told of Moses's youth.
    relate(sammy, moses_youth, lambda a, b: a == b + 3, "sammy")

    return model, {
        "ages": ages,
        "children": children,
        "countries": countries,
        "stories": stories,
    }
