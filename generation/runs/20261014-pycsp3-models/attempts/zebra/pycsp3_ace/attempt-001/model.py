from pycsp3 import *

# each attribute value is the house (0 to 4, from the left) where it is found
# colors: yellow, green, red, white, blue
colors = VarArray(size=5, dom=range(5))
# nations: italy, spain, japan, england, norway
nations = VarArray(size=5, dom=range(5))
# pets: cat, zebra, bear, snails, horse
pets = VarArray(size=5, dom=range(5))
# drinks: milk, water, tea, coffee, juice
drinks = VarArray(size=5, dom=range(5))
# jobs: painter, sculptor, diplomat, pianist, doctor
jobs = VarArray(size=5, dom=range(5))

yellow, green, red, white, blue = colors
italy, spain, japan, england, norway = nations
cat, zebra, bear, snails, horse = pets
milk, water, tea, coffee, juice = drinks
painter, sculptor, diplomat, pianist, doctor = jobs

satisfy(
    # all the attributes of one kind are in different houses
    AllDifferent(colors),
    AllDifferent(nations),
    AllDifferent(pets),
    AllDifferent(drinks),
    AllDifferent(jobs),
    # the Englishman lives in the red house
    england == red,
    # the Spaniard is a painter
    spain == painter,
    # the Japanese is a diplomat
    japan == diplomat,
    # the Italian lives in the red, white or green house
    Or(italy == red, italy == white, italy == green),
    # the Norwegian owns the zebra
    norway == zebra,
    # the painter owns the horse
    painter == horse,
    # the diplomat drinks coffee
    diplomat == coffee,
    # the one who drinks milk lives in the white house
    milk == white,
    # the doctor drinks milk
    doctor == milk,
    # the snails are owned by the sculptor
    snails == sculptor,
    # the green house is immediately on the left of the red one
    green + 1 == red,
    # the Norwegian lives immediately on the right of the blue house
    norway == blue + 1,
    # the green house is next to the white one
    abs(green - white) == 1,
    # the horse is owned by the neighbour of the diplomat
    abs(horse - diplomat) == 1,
)
