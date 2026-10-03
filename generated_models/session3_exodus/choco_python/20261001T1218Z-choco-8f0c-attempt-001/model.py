# Exodus: five children of different ages, from different countries, each told a different part of
# the Exodus story. Match age, child, country and story from five clues.
from pychoco.model import Model

# The puzzle has no instance data; the entities and the clues are its statement.
AGE_VALUES = [3, 5, 7, 8, 10]  # the ages, in the order of the ages list
N = 5


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # Every entity gets a group number 1..5; entities with the same number belong together.
    def group(prefix):
        return [model.intvar(1, N, name=f"{prefix}_{k}") for k in range(N)]

    ages = group("age")  # three, five, seven, eight, ten
    children = group("child")
    bernice, carl, debby, sammy, ted = children
    countries = group("country")
    ethiopia, kazakhstan, lithuania, morocco, yemen = countries
    stories = group("story")
    burning_bush, captivity, moses_youth, passover, ten_commandments = stories

    # Within each category, every entity is in a different group.
    for category in (ages, children, countries, stories):
        model.all_different(category).post()

    def age_of(entity, name):
        """The age (3..10) of the group the entity is in: entity == ages[slot], age = AGE_VALUES[slot]."""
        slot = model.intvar(0, N - 1, name=f"slot_{name}")
        model.element(entity, ages, slot).post()
        value = model.intvar(min(AGE_VALUES), max(AGE_VALUES), name=f"age_{name}")
        model.element(value, AGE_VALUES, slot).post()
        return value

    # 1. Debby's family is from Lithuania.
    model.arithm(debby, "=", lithuania).post()
    # 2. The child who told the Passover story is two years older than Bernice.
    model.arithm(age_of(passover, "passover"), "-", age_of(bernice, "bernice"), "=", 2).post()
    # 3. The child from Yemen is younger than the child from Ethiopia.
    model.arithm(age_of(yemen, "yemen"), "<", age_of(ethiopia, "ethiopia")).post()
    # 4. The child from Morocco is three years older than Ted.
    model.arithm(age_of(morocco, "morocco"), "-", age_of(ted, "ted"), "=", 3).post()
    # 5. Sammy is three years older than the child who told of Moses's youth.
    model.arithm(age_of(sammy, "sammy"), "-", age_of(moses_youth, "moses_youth"), "=", 3).post()

    return model, {"ages": ages, "children": children, "countries": countries, "stories": stories}
