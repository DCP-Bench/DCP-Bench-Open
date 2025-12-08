#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/jobs_puzzle.py

"""
Four people hold eight different jobs. Each person holds exactly two jobs.
The jobs are: chef, guard, nurse, clerk, police officer, teacher, actor, and boxer.

Clues:
1. The nurse is not a teacher, police officer, or clerk.
2. The clerk is not the chef.
3. Person 0 is not the boxer.
4. Person 3 is not the teacher, police officer, or nurse.
5. Person 0, the chef, and the police officer went golfing together.

Determine which person holds which two jobs.

Print the person index, 0-3, assigned to each job (chef, guard, nurse, clerk, police_officer, teacher, actor, boxer).
"""

# Import libraries
from cpmpy import *
import json

num_people = 4
num_jobs = 8

# Variables
# jobs[i] is the person assigned to job i.
jobs = intvar(0, num_people - 1, shape=num_jobs, name="jobs")
chef, guard, nurse, clerk, police_officer, teacher, actor, boxer = jobs

# Constraints
model = Model()

# Each person holds exactly two jobs.
for i in range(num_people):
    model += [sum(jobs == i) == 2]

# 1. The nurse is not a teacher, police officer, or clerk.
model += [nurse != teacher]
model += [nurse != police_officer]
model+= [nurse != clerk]

# 2. The clerk is not the chef
model += [clerk != chef]

# 3. Person 0 is not the boxer.
model += [boxer != 0]

# 4. Person 3 is not the teacher, police officer, or nurse.
model += [teacher != 3]
model += [police_officer != 3]
model += [nurse != 3]

# 5. Person 0, the chef, and the police officer are distinct.
model += [chef != 0]
model += [police_officer != 0]
model += [chef != police_officer]

# Solve
model.solve()

# Output
solution = {
    "chef": chef.value(), "guard": guard.value(), "nurse": nurse.value(),
    "clerk": clerk.value(), "police_officer": police_officer.value(),
    "teacher": teacher.value(), "actor": actor.value(), "boxer": boxer.value()
}
print(json.dumps(solution, indent=4))
# End of CPMPy script