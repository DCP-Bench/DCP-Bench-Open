from cpmpy import *
import json

# Decision Variables
# We'll model 5 dice, each with 6 faces (standard dice)
dice = intvar(1, 6, shape=(5,6), name="dice")  # 5 dice, each with 6 faces

# Model
model = Model()

# Helper function to calculate probability that die A beats die B
def prob_beat(model, A, B):
    # Create a binary variable for each face comparison
    beats = boolvar(shape=(6,6))
    for a in range(6):
        for b in range(6):
            model += (beats[a,b] == (A[a] > B[b]))
    # More than half of 36 possible combinations must be true
    return sum(beats) > 18

# Constraints for the nontransitive relationships
# Rock(1) crushes Scissors(3)
model += prob_beat(model, dice[0], dice[2])
# Rock(1) crushes Lizard(4)
model += prob_beat(model, dice[0], dice[3])
# Paper(2) covers Rock(1)
model += prob_beat(model, dice[1], dice[0])
# Paper(2) disproves Spock(5)
model += prob_beat(model, dice[1], dice[4])
# Scissors(3) cuts Paper(2)
model += prob_beat(model, dice[2], dice[1])
# Scissors(3) decapitate Lizard(4)
model += prob_beat(model, dice[2], dice[3])
# Lizard(4) eats Paper(2)
model += prob_beat(model, dice[3], dice[1])
# Lizard(4) poisons Spock(5)
model += prob_beat(model, dice[3], dice[4])
# Spock(5) vaporizes Rock(1)
model += prob_beat(model, dice[4], dice[0])
# Spock(5) smashes Scissors(3)
model += prob_beat(model, dice[4], dice[2])

# Solve
model.solve()

# Print solution
solution = {
    "dice": dice.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script