
import cpmpy as cp
import json

# Jobs: chef, guard, nurse, clerk, police_officer, teacher, actor, boxer
model = cp.Model()

# Decision variables: which person (0-3) holds each job
chef = cp.intvar(0, 3, name="chef")
guard = cp.intvar(0, 3, name="guard")
nurse = cp.intvar(0, 3, name="nurse")
clerk = cp.intvar(0, 3, name="clerk")
police_officer = cp.intvar(0, 3, name="police_officer")
teacher = cp.intvar(0, 3, name="teacher")
actor = cp.intvar(0, 3, name="actor")
boxer = cp.intvar(0, 3, name="boxer")

jobs = [chef, guard, nurse, clerk, police_officer, teacher, actor, boxer]

# Each person holds exactly two jobs
for p in range(4):
    model += cp.Count(jobs, p) == 2

# Clues as constraints:
# 1. The nurse is not a teacher, police officer, or clerk.
model += teacher != nurse
model += police_officer != nurse
model += clerk != nurse

# 2. The clerk is not the chef.
model += clerk != chef

# 3. Person 0 is not the boxer.
model += boxer != 0

# 4. Person 3 is not the teacher, police officer, or nurse.
model += teacher != 3
model += police_officer != 3
model += nurse != 3

# 5. Person 0, the chef, and the police officer went golfing together.
# They are three distinct people, and neither chef nor police_officer is person 0.
model += chef != 0
model += police_officer != 0
model += chef != police_officer

# Solve and print
if model.solve():
    solution = {
        'chef': int(chef.value()),
        'guard': int(guard.value()),
        'nurse': int(nurse.value()),
        'clerk': int(clerk.value()),
        'police_officer': int(police_officer.value()),
        'teacher': int(teacher.value()),
        'actor': int(actor.value()),
        'boxer': int(boxer.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
