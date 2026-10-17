# Zebra puzzle (Einstein's puzzle): five houses in a row, numbered 0 (left) to 4 (right).
# Each inhabitant attribute (colour, nation, pet, drink, job) is given as the house
# index of each of its five values. The same index means the same house.
import cvc5.pythonic as cz


def build(instance):
    yellow, green, red, white, blue = cz.Ints("yellow green red white blue")
    italy, spain, japan, england, norway = cz.Ints("italy spain japan england norway")
    cat, zebra, bear, snails, horse = cz.Ints("cat zebra bear snails horse")
    milk, water, tea, coffee, juice = cz.Ints("milk water tea coffee juice")
    painter, sculptor, diplomat, pianist, doctor = cz.Ints("painter sculptor diplomat pianist doctor")

    colors = [yellow, green, red, white, blue]
    nations = [italy, spain, japan, england, norway]
    pets = [cat, zebra, bear, snails, horse]
    drinks = [milk, water, tea, coffee, juice]
    jobs = [painter, sculptor, diplomat, pianist, doctor]

    constraints = []

    # Each of the five houses is painted a different color, and has one inhabitant.
    # The inhabitants are all of different nationalities, own different pets,
    # drink different beverages and have different jobs.
    for group in (colors, nations, pets, drinks, jobs):
        for v in group:
            constraints.append(v >= 0)
            constraints.append(v <= 4)
        constraints.append(cz.Distinct(group))

    # the painter owns the horse
    constraints.append(jobs[0] == pets[4])
    # the diplomat drinks coffee
    constraints.append(jobs[2] == drinks[3])
    # the one who drinks milk lives in the white house
    constraints.append(drinks[0] == colors[3])
    # the Spaniard is a painter
    constraints.append(nations[1] == jobs[0])
    # the Englishman lives in the red house
    constraints.append(nations[3] == colors[2])
    # the snails are owned by the sculptor
    constraints.append(pets[3] == jobs[1])
    # the green house is immediately on the left of the red one
    constraints.append(colors[1] + 1 == colors[2])
    # the Norwegian lives immediately on the right of the blue house
    constraints.append(nations[4] == colors[4] + 1)
    # the doctor drinks milk
    constraints.append(jobs[4] == drinks[0])
    # the diplomat is Japanese
    constraints.append(jobs[2] == nations[2])
    # the Norwegian owns the zebra
    constraints.append(nations[4] == pets[1])
    # the green house is next to the white one
    constraints.append(cz.Or(colors[1] == colors[3] + 1, colors[3] == colors[1] + 1))
    # the horse is owned by the neighbor of the diplomat
    constraints.append(cz.Or(pets[4] == jobs[2] + 1, jobs[2] == pets[4] + 1))
    # the Italian either lives in the red, white or green house
    constraints.append(cz.Or(nations[0] == colors[2], nations[0] == colors[3], nations[0] == colors[1]))

    outputs = {
        "colors": colors,
        "drinks": drinks,
        "jobs": jobs,
        "nations": nations,
        "pets": pets,
    }
    return constraints, outputs
