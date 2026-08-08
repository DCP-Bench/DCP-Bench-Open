
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# nationality encoding: 0 = American, 1 = English, 2 = French
# person indices: 0 = X, 1 = Y, 2 = Z

# x, y, z : nationality of person X, Y, Z respectively (values 0..2)
x = cp.intvar(0, 2, name="x")
y = cp.intvar(0, 2, name="y")
z = cp.intvar(0, 2, name="z")
person_nat = [x, y, z]

# american, english, french : index of the person (0=X,1=Y,2=Z) having that nationality
american = cp.intvar(0, 2, name="american")
english = cp.intvar(0, 2, name="english")
french = cp.intvar(0, 2, name="french")
nat_person = [american, english, french]

# Passing mapping: succ[i] is the person index who receives cards from person i
# (i.e., the person i passed to - the person on their right).
succ = cp.intvar(0, 2, shape=3, name="succ")

# Auxiliary variable: index of the person who passed to the Frenchwoman
pred_french = cp.intvar(0, 2, name="pred_french")

# Constraints

# 1) x,y,z are a permutation of {0,1,2} (each person has distinct nationality)
model += cp.AllDifferent(person_nat)

# 2) american,english,french are a permutation of {0,1,2} (each nationality assigned to a distinct person)
model += cp.AllDifferent(nat_person)

# 3) Link the two representations as inverse permutations:
#    person_nat[i] = j  <->  nat_person[j] = i
model += cp.Inverse(person_nat, nat_person)

# 4) Succ is a permutation without fixed points (each passes to someone else).
#    For 3 people, this enforces a 3-cycle (pass-to-right around the table).
model += cp.AllDifferent(succ)
for i in range(3):
    model += (succ[i] != i)

# 5) Y passed three hearts to the American.
#    The recipient of Y (person index 1) is the American.
model += (succ[1] == american)

# 6) pred_french is the person who passed to the Frenchwoman.
model += (succ[pred_french] == french)

# 7) X passed the queen... to the person who passed their cards to the Frenchwoman.
#    The recipient of X (person index 0) is exactly that person (pred_french).
model += (succ[0] == pred_french)

# Solve and print
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
