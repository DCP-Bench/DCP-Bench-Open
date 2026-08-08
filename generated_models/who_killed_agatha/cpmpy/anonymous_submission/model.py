# Import libraries
from cpmpy import *
import json

# Parameters
names = ["Agatha herself", "the butler", "Charles"]
n = len(names)

# Decision Variables
killer = intvar(0, n-1, name="killer")  # Index of the killer (0: Agatha, 1: butler, 2: Charles)

# Create variables for hates and richer relations
# hates[i,j] = True if person i hates person j
hates = boolvar(shape=(n, n), name="hates")
# richer[i,j] = True if person i is richer than person j
richer = boolvar(shape=(n, n), name="richer")

# Model
model = Model()

# A killer always hates, and is no richer than his victim
model += (killer == 0).implies(hates[0,0])  # if Agatha is killer, she hates herself
model += (killer == 1).implies(hates[1,0])  # if butler is killer, he hates Agatha
model += (killer == 2).implies(hates[2,0])  # if Charles is killer, he hates Agatha
model += (killer == 0).implies(~richer[0,0])  # if Agatha is killer, not richer than herself
model += (killer == 1).implies(~richer[1,0])  # if butler is killer, not richer than Agatha
model += (killer == 2).implies(~richer[2,0])  # if Charles is killer, not richer than Agatha

# Charles hates noone that Agatha hates
for j in range(n):
    model += hates[0,j].implies(~hates[2,j])  # Charles is index 2

# Agatha hates everybody except the butler
model += hates[0,0] == False  # Agatha doesn't hate herself
model += hates[0,1] == False  # Agatha doesn't hate the butler
model += hates[0,2] == True   # Agatha hates Charles

# The butler hates everyone not richer than Aunt Agatha
for j in range(n):
    model += (~richer[j,0]).implies(hates[1,j])  # butler is index 1

# The butler hates everyone whom Agatha hates
for j in range(n):
    model += hates[0,j].implies(hates[1,j])

# Noone hates everyone
for i in range(n):
    model += sum(hates[i,j] for j in range(n)) < n  # at least one person not hated by i

# Solve
model.solve()

# Print solution
solution = {
    "killer": int(killer.value())
}
print(json.dumps(solution))