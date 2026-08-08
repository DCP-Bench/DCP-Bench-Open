
import cpmpy as cp
import json

# Data
persons = range(4)
job_names = ['chef', 'guard', 'nurse', 'clerk', 'police_officer', 'teacher', 'actor', 'boxer']
idx = {name: i for i, name in enumerate(job_names)}
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# jobs[j] = person index (0..3) assigned to job j
jobs = cp.intvar(0, 3, shape=len(job_names), name="jobs")

# Constraints

# Each person holds exactly two jobs
for p in persons:
    model += (cp.Count(jobs, p) == 2)

# 1. The nurse is not a teacher, police officer, or clerk.
model += (jobs[idx['nurse']] != jobs[idx['teacher']])
model += (jobs[idx['nurse']] != jobs[idx['police_officer']])
model += (jobs[idx['nurse']] != jobs[idx['clerk']])

# 2. The clerk is not the chef.
model += (jobs[idx['clerk']] != jobs[idx['chef']])

# 3. Person 0 is not the boxer.
model += (jobs[idx['boxer']] != 0)

# 4. Person 3 is not the teacher, police officer, or nurse.
model += (jobs[idx['teacher']] != 3)
model += (jobs[idx['police_officer']] != 3)
model += (jobs[idx['nurse']] != 3)

# 5. Person 0, the chef, and the police officer went golfing together.
#    They are three distinct people.
model += (jobs[idx['chef']] != 0)
model += (jobs[idx['police_officer']] != 0)
model += (jobs[idx['chef']] != jobs[idx['police_officer']])

# Objective (none)

# Solve and print
if model.solve():
    solution = {
        'chef': int(jobs[idx['chef']].value()),
        'guard': int(jobs[idx['guard']].value()),
        'nurse': int(jobs[idx['nurse']].value()),
        'clerk': int(jobs[idx['clerk']].value()),
        'police_officer': int(jobs[idx['police_officer']].value()),
        'teacher': int(jobs[idx['teacher']].value()),
        'actor': int(jobs[idx['actor']].value()),
        'boxer': int(jobs[idx['boxer']].value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
