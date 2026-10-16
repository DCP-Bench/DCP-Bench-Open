from pycsp3 import *

# Farmer and cows: cows numbered 1 to num_cows give milk equal to their number. The farmer
# shares the cows among his sons so that each son gets the given number of cows and
# the same total quantity of milk.
num_cows = data.num_cows
num_sons = data.num_sons
cows_per_son = data.cows_per_son

# cow_assignments[i] is the son who gets cow i+1
cow_assignments = VarArray(size=num_cows, dom=range(num_sons))

# every son gets the number of cows given for him
satisfy(
    [Count(cow_assignments, value=s) == cows_per_son[s] for s in range(num_sons)],
)

# the total milk of all cows, shared equally among the sons
total_milk = num_cows * (num_cows + 1) // 2
milk_per_son = total_milk // num_sons

satisfy(
    # the milk of the cows a son gets adds up to the same quantity for each son
    [Sum((cow_assignments[i] == s) * (i + 1) for i in range(num_cows)) == milk_per_son
     for s in range(num_sons)],
)
