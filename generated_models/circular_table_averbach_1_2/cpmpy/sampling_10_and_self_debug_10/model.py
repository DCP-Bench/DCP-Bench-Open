
import cpmpy as cp
import json

# We have 3 players: X, Y, Z, and 3 nationalities: American, English, French.
# Assign integers 0,1,2 to players and nationalities.
# We want to find a mapping between players and nationalities.
# Variables x, y, z represent the nationality of player X, Y, Z respectively.
# Variables american, english, french represent the player who is American, English, French respectively.
# The value of x, y, z, american, english, french is in {0,1,2} and represents the index (player or nationality).

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, 2, name="x")  # nationality of player X
y = cp.intvar(0, 2, name="y")  # nationality of player Y
z = cp.intvar(0, 2, name="z")  # nationality of player Z

american = cp.intvar(0, 2, name="american")  # player who is American
english = cp.intvar(0, 2, name="english")  # player who is English
french = cp.intvar(0, 2, name="french")  # player who is French

players = [x, y, z]
nationalities = [american, english, french]

# Constraints
# All players have different nationalities (one-to-one)
model += cp.AllDifferent(players)
model += cp.AllDifferent(nationalities)

# Link players and nationalities (inverse mapping)
# nationality of player i = j iff nationality j is player i
model += cp.Inverse(players, nationalities)

# Circular seating order: Players are seated around a table, passing cards to the right:
# Passing to the right means the recipient is the player to the left in the order.
# Let's define the seating order as X->Y->Z->X clockwise.
# Then to the right means passing cards to the person on their right:
# X passes to Z
# Y passes to X
# Z passes to Y

# Clue 1: Y passed three hearts to the American.
# That means Y passed to the American player.
# Y passes to X (to right), so X must be American.
model += x == american

# Clue 2: X passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman.
# X passes to Z (to right)
# The person who passed cards to the Frenchwoman passes to Frenchwoman (to right).
# The person who passed cards to the Frenchwoman is the one who passed cards to french.
# Who passed cards to Frenchwoman? The player to the left of Frenchwoman.
# Passing to right means right neighbor is recipient.
# So if Frenchwoman is nationality of player p, then the person who passed cards to Frenchwoman is the player to the left of p.
# Seating order: X->Y->Z->X clockwise.
# Left of a player is the one who receives cards from that player.
# Since passing to right means passing to the right neighbor, the player who passed cards to Frenchwoman is the player to the left of the Frenchwoman.

# To identify the player who passed cards to Frenchwoman:
# If french = p (player index), then the player who passed cards to Frenchwoman is the player to the left of p:
# Left of X(0) is Y(1)
# Left of Y(1) is Z(2)
# Left of Z(2) is X(0)

# The person who passed cards to Frenchwoman is left_of_french = (french + 1) % 3
# X passed queen of spades and two diamonds to that person.
# X passes to Z
# So X passes to Z, and the person who passed cards to Frenchwoman is the recipient of X's cards,
# so that person must be Z.

# Therefore, left_of_french == Z (2)
model += (french + 1) % 3 == 2

# Print the values of X, Y, Z, American, English, French (x, y, z, american, english, french)
if model.solve():
    solution = {
        'x': int(x.value()),
        'y': int(y.value()),
        'z': int(z.value()),
        'american': int(american.value()),
        'english': int(english.value()),
        'french': int(french.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
