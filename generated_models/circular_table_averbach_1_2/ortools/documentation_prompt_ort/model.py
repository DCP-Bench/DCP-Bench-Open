from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# We have three players: X, Y, Z
# and three nationalities: American, English, French
# We represent each by an integer 0, 1, or 2
# The same integer value means the player has that nationality

# Decision variables
x = model.NewIntVar(0, 2, 'x')
y = model.NewIntVar(0, 2, 'y')
z = model.NewIntVar(0, 2, 'z')

american = model.NewIntVar(0, 2, 'american')
english = model.NewIntVar(0, 2, 'english')
french = model.NewIntVar(0, 2, 'french')

# All players have different nationalities
model.AddAllDifferent([x, y, z])
model.AddAllDifferent([american, english, french])

# The nationality variables are a permutation of players
# So the set {american, english, french} is the same as {x, y, z}
# We enforce that the set of nationalities equals the set of players
# This can be done by ensuring that the three nationality variables are a permutation of x,y,z
# We can do this by enforcing that the set of nationality variables equals the set of player variables
# Since all are distinct, we can enforce that the sorted lists are equal
# But CP-SAT does not have direct set constraints, so we enforce that the nationality variables are a permutation of x,y,z
# We can do this by adding allowed assignments for (american, english, french) as permutations of (x,y,z)
# But since x,y,z are variables, we use a trick: we add constraints that each nationality variable equals one of x,y,z and all different

# Enforce that american, english, french are a permutation of x,y,z
# So each nationality variable equals one of x,y,z
model.AddAllowedAssignments([american], [[0],[1],[2]])
model.AddAllowedAssignments([english], [[0],[1],[2]])
model.AddAllowedAssignments([french], [[0],[1],[2]])

# All different already enforced for nationality variables
# So nationality variables are a permutation of 0,1,2
# Similarly for players

# Now the clues:

# Seating is around a circular table: each player passes cards to the person on their right.
# The order of players around the table is circular.
# We need to define the seating order to interpret "passed to the person on their right"

# Let's define the seating order as a permutation of [x, y, z] in positions 0,1,2 around the table
# But we don't know the order, so let's define positions for each player

# Let's define position variables for each player: pos_x, pos_y, pos_z in {0,1,2}
pos_x = model.NewIntVar(0, 2, 'pos_x')
pos_y = model.NewIntVar(0, 2, 'pos_y')
pos_z = model.NewIntVar(0, 2, 'pos_z')

model.AddAllDifferent([pos_x, pos_y, pos_z])

# The players are seated in positions 0,1,2 around the table clockwise
# The person on the right of position i is position (i-1) mod 3 (assuming clockwise seating)
# Because if we number seats clockwise 0,1,2, then the right neighbor of seat i is seat (i-1) mod 3

# We need to model the passing of cards:
# Each player passes three cards to the person on their right.

# Clue 1: Y passed three hearts to the American.
# So the person on the right of Y is American.

# Clue 2: X passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman.

# Let's analyze clue 2 carefully:
# "X passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman."

# So X passed cards to a person P.
# P passed cards to the Frenchwoman.

# So the person who received cards from X is the person who passed cards to the Frenchwoman.

# Since passing is to the right, the person who passed cards to the Frenchwoman is the person on the left of the Frenchwoman.

# So the person who received cards from X is the person on the left of the Frenchwoman.

# Let's define the person who received cards from X:
# The person on the right of X is the person who received cards from X.

# So person_on_right(X) = person who passed cards to Frenchwoman = person_on_left(Frenchwoman)

# So person_on_right(X) = person_on_left(Frenchwoman)

# Since the table is circular with positions 0,1,2, and right neighbor of i is (i-1) mod 3,
# left neighbor of i is (i+1) mod 3.

# So person_on_right(X) = person with position (pos_x - 1) mod 3
# person_on_left(Frenchwoman) = person with position (pos_french + 1) mod 3

# We need to find the player who is at position (pos_x - 1) mod 3 and the player who is at position (pos_french + 1) mod 3
# and enforce they are the same player.

# First, find pos_french: position of the Frenchwoman
# Frenchwoman is one of the players x,y,z with nationality french

# So we need to link nationality to player positions.

# Let's create arrays for players and their positions and nationalities:
players = [x, y, z]
positions = [pos_x, pos_y, pos_z]
nationalities = [american, english, french]

# We need to find pos_french: position of the player whose nationality is french

# We can create a variable pos_french in {0,1,2}
pos_french = model.NewIntVar(0, 2, 'pos_french')

# For each player i in {0,1,2}, if nationality of player i == french, then pos_i == pos_french

# We create boolean variables for each player i indicating if that player is french
is_french = []
for i in range(3):
    b = model.NewBoolVar(f'is_french_{i}')
    model.Add(players[i] == french).OnlyEnforceIf(b)
    model.Add(players[i] != french).OnlyEnforceIf(b.Not())
    model.Add(positions[i] == pos_french).OnlyEnforceIf(b)
    is_french.append(b)

# Exactly one player is french
model.AddExactlyOne(is_french)

# Similarly, find the player at position (pos_x - 1) mod 3: person_on_right_x
person_on_right_x = model.NewIntVar(0, 2, 'person_on_right_x')

# Similarly, person_on_left_french = player at position (pos_french + 1) mod 3
person_on_left_french = model.NewIntVar(0, 2, 'person_on_left_french')

# We need to link positions to players:
# For person_on_right_x: find player i with positions[i] == (pos_x - 1) mod 3
# For person_on_left_french: find player i with positions[i] == (pos_french + 1) mod 3

# Since mod 3 arithmetic is involved, define helper variables for (pos_x - 1) mod 3 and (pos_french + 1) mod 3
pos_x_minus_1 = model.NewIntVar(0, 2, 'pos_x_minus_1')
pos_french_plus_1 = model.NewIntVar(0, 2, 'pos_french_plus_1')

model.Add(pos_x_minus_1 == (pos_x + 2) % 3)
model.Add(pos_french_plus_1 == (pos_french + 1) % 3)

# Now, for person_on_right_x:
# person_on_right_x == player i such that positions[i] == pos_x_minus_1
# Similarly for person_on_left_french

# We can use element constraints:
# Create arrays for players and positions
# We want to find player i where positions[i] == pos_x_minus_1

# Since positions are variables, we can create boolean indicators for each player i:
right_x_candidates = []
left_french_candidates = []
for i in range(3):
    b_right = model.NewBoolVar(f'right_x_candidate_{i}')
    model.Add(positions[i] == pos_x_minus_1).OnlyEnforceIf(b_right)
    model.Add(positions[i] != pos_x_minus_1).OnlyEnforceIf(b_right.Not())
    right_x_candidates.append(b_right)

    b_left = model.NewBoolVar(f'left_french_candidate_{i}')
    model.Add(positions[i] == pos_french_plus_1).OnlyEnforceIf(b_left)
    model.Add(positions[i] != pos_french_plus_1).OnlyEnforceIf(b_left.Not())
    left_french_candidates.append(b_left)

# Exactly one candidate for each
model.AddExactlyOne(right_x_candidates)
model.AddExactlyOne(left_french_candidates)

# person_on_right_x == sum over i of b_right[i] * players[i]
# person_on_left_french == sum over i of b_left[i] * players[i]

# Since players[i] are variables, we can use linear expressions
model.Add(person_on_right_x == sum(right_x_candidates[i] * players[i] for i in range(3)))
model.Add(person_on_left_french == sum(left_french_candidates[i] * players[i] for i in range(3)))

# Now enforce the clue:
# person_on_right_x == person_on_left_french
model.Add(person_on_right_x == person_on_left_french)

# Clue 1: Y passed three hearts to the American.
# The person on the right of Y is American.

# person_on_right_y = player at position (pos_y - 1) mod 3
pos_y_minus_1 = model.NewIntVar(0, 2, 'pos_y_minus_1')
model.Add(pos_y_minus_1 == (pos_y + 2) % 3)

right_y_candidates = []
for i in range(3):
    b = model.NewBoolVar(f'right_y_candidate_{i}')
    model.Add(positions[i] == pos_y_minus_1).OnlyEnforceIf(b)
    model.Add(positions[i] != pos_y_minus_1).OnlyEnforceIf(b.Not())
    right_y_candidates.append(b)

model.AddExactlyOne(right_y_candidates)

person_on_right_y = model.NewIntVar(0, 2, 'person_on_right_y')
model.Add(person_on_right_y == sum(right_y_candidates[i] * players[i] for i in range(3)))

# The person on the right of Y is American
model.Add(person_on_right_y == american)

# All variables are in 0..2, all different for players and nationalities

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': solver.Value(x),
        'y': solver.Value(y),
        'z': solver.Value(z),
        'american': solver.Value(american),
        'english': solver.Value(english),
        'french': solver.Value(french)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")