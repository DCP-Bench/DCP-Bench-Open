
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: house numbers 1 to 5
yellow  = cp.IntVar(1, 5, name="yellow")
green   = cp.IntVar(1, 5, name="green")
red     = cp.IntVar(1, 5, name="red")
white   = cp.IntVar(1, 5, name="white")
blue    = cp.IntVar(1, 5, name="blue")

italy   = cp.IntVar(1, 5, name="italy")
spain   = cp.IntVar(1, 5, name="spain")
japan   = cp.IntVar(1, 5, name="japan")
england = cp.IntVar(1, 5, name="england")
norway  = cp.IntVar(1, 5, name="norway")

cat     = cp.IntVar(1, 5, name="cat")
zebra   = cp.IntVar(1, 5, name="zebra")
bear    = cp.IntVar(1, 5, name="bear")
snails  = cp.IntVar(1, 5, name="snails")
horse   = cp.IntVar(1, 5, name="horse")

milk    = cp.IntVar(1, 5, name="milk")
water   = cp.IntVar(1, 5, name="water")
tea     = cp.IntVar(1, 5, name="tea")
coffee  = cp.IntVar(1, 5, name="coffee")
juice   = cp.IntVar(1, 5, name="juice")

painter   = cp.IntVar(1, 5, name="painter")
sculptor  = cp.IntVar(1, 5, name="sculptor")
diplomat  = cp.IntVar(1, 5, name="diplomat")
pianist   = cp.IntVar(1, 5, name="pianist")
doctor    = cp.IntVar(1, 5, name="doctor")

# All-different constraints
model += cp.all_different([yellow, green, red, white, blue])
model += cp.all_different([italy, spain, japan, england, norway])
model += cp.all_different([cat, zebra, bear, snails, horse])
model += cp.all_different([milk, water, tea, coffee, juice])
model += cp.all_different([painter, sculptor, diplomat, pianist, doctor])

# Clues
model += (painter == horse)                    # The painter owns the horse
model += (diplomat == coffee)                  # The diplomat drinks coffee
model += (milk == white)                       # The one who drinks milk lives in the white house
model += (spain == painter)                    # The Spaniard is a painter
model += (england == red)                      # The Englishman lives in the red house
model += (sculptor == snails)                  # The snails are owned by the sculptor
model += (green < red)                         # The green house is on the left of the red one
model += (cp.abs(green - white) == 1)          # The green house is next to the white one
model += (norway > blue)                       # The Norwegian lives on the right of the blue house
model += (doctor == milk)                      # The doctor drinks milk
model += (diplomat == japan)                   # The diplomat is Japanese
model += (norway == zebra)                     # The Norwegian owns the zebra
model += (cp.abs(horse - diplomat) == 1)        # The horse is owned by the neighbor of the diplomat

# The Italian either lives in the red, white or green house
model += cp.sum([
    italy == red,
    italy == white,
    italy == green
]) >= 1

# Solve and print
if model.solve():
    colors  = [int(yellow.value()), int(green.value()), int(red.value()),
               int(white.value()), int(blue.value())]
    nations = [int(italy.value()), int(spain.value()), int(japan.value()),
               int(england.value()), int(norway.value())]
    pets    = [int(cat.value()), int(zebra.value()), int(bear.value()),
               int(snails.value()), int(horse.value())]
    drinks  = [int(milk.value()), int(water.value()), int(tea.value()),
               int(coffee.value()), int(juice.value())]
    jobs    = [int(painter.value()), int(sculptor.value()), int(diplomat.value()),
               int(pianist.value()), int(doctor.value())]
    solution = {
        "colors": colors,
        "nations": nations,
        "pets": pets,
        "drinks": drinks,
        "jobs": jobs
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
