# Import libraries
from cpmpy import *
import json

# Parameters
n_teams = 9
n_days = 18
teams = ["Clem", "Duke", "FSU", "GT", "UMD", "UNC", "NCSt", "UVA", "Wake"]
mirroring_scheme = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]
rival_pairs = [("Duke", "UNC"), ("Clem", "GT"), ("NCSt", "Wake"), ("UMD", "UVA")]

# Decision Variables
config = intvar(0, n_teams-1, shape=(n_days, n_teams), name="config")  # Match configuration
where = intvar(0, 2, shape=(n_days, n_teams), name="where")  # 0=home, 1=away, 2=bye

# Model
model = Model()

# Double round robin constraints
for t1 in range(n_teams):
    for t2 in range(n_teams):
        if t1 != t2:
            # Each team plays every other team exactly twice (once home, once away)
            home_games = sum((config[d, t1] == t2) & (where[d, t1] == 0) for d in range(n_days))
            away_games = sum((config[d, t2] == t1) & (where[d, t2] == 1) for d in range(n_days))
            model += home_games == 1
            model += away_games == 1

# Mirroring constraint
for (r1, r2) in mirroring_scheme:
    for t in range(n_teams):
        model += config[r1-1, t] == config[r2-1, t]

# No Two Final Aways
for t in range(n_teams):
    model += (where[n_days-1, t] != 1) | (where[n_days-2, t] != 1)

# Home/Away/Bye Pattern Constraints
for t in range(n_teams):
    for d in range(n_days-2):
        # No more than two away matches in a row
        model += (where[d, t] != 1) | (where[d+1, t] != 1) | (where[d+2, t] != 1)
        # No more than two home matches in a row
        model += (where[d, t] != 0) | (where[d+1, t] != 0) | (where[d+2, t] != 0)
    for d in range(n_days-3):
        # No more than three away matches or byes in a row
        model += (where[d, t] == 0) | (where[d+1, t] == 0) | (where[d+2, t] == 0) | (where[d+3, t] == 0)
    for d in range(n_days-4):
        # No more than four home matches or byes in a row
        model += (where[d, t] == 1) | (where[d+1, t] == 1) | (where[d+2, t] == 1) | (where[d+3, t] == 1) | (where[d+4, t] == 1)

# Weekend Pattern
weekend_days = [d for d in range(1, n_days+1) if d % 2 == 0]
for t in range(n_teams):
    home_weekends = sum(where[d-1, t] == 0 for d in weekend_days)
    away_weekends = sum(where[d-1, t] == 1 for d in weekend_days)
    bye_weekends = sum(where[d-1, t] == 2 for d in weekend_days)
    model += home_weekends == 4
    model += away_weekends == 4
    model += bye_weekends == 1

# First Weekends
first_weekends = [d for d in range(1, 6) if d % 2 == 0]
for t in range(n_teams):
    model += sum(where[d-1, t] != 1 for d in first_weekends) >= 2

# Rival Matches
for (t1, t2) in rival_pairs:
    t1_idx = teams.index(t1)
    t2_idx = teams.index(t2)
    model += (config[n_days-1, t1_idx] == t2_idx) | (config[n_days-1, t1_idx] == teams.index("FSU")) | (where[n_days-1, t1_idx] == 2)
    model += (config[n_days-1, t2_idx] == t1_idx) | (config[n_days-1, t2_idx] == teams.index("FSU")) | (where[n_days-1, t2_idx] == 2)

# Constrained Matches
constrained_pairs = [("Wake", "UNC"), ("Wake", "Duke"), ("GT", "UNC"), ("GT", "Duke")]
for (t1, t2) in constrained_pairs:
    t1_idx = teams.index(t1)
    t2_idx = teams.index(t2)
    model += sum((config[d, t1_idx] == t2_idx) | (config[d, t2_idx] == t1_idx) for d in range(10, 18)) >= 1

# Opponent Sequence Constraints
for t in range(n_teams):
    for d in range(n_days-1):
        model += ~((config[d, t] == teams.index("UNC")) & (where[d, t] == 1) & (config[d+1, t] == teams.index("Duke")) & (where[d+1, t] == 1))
    for d in range(n_days-2):
        model += ~((config[d, t] == teams.index("UNC")) & (config[d+1, t] == teams.index("Duke")) & (config[d+2, t] == teams.index("Wake")))

# Other Constraints
unc_idx = teams.index("UNC")
duke_idx = teams.index("Duke")
wake_idx = teams.index("Wake")
clem_idx = teams.index("Clem")
fsu_idx = teams.index("FSU")
gt_idx = teams.index("GT")
umd_idx = teams.index("UMD")
ncst_idx = teams.index("NCSt")
uva_idx = teams.index("UVA")

# UNC plays Duke in last date and date 11
model += config[n_days-1, unc_idx] == duke_idx
model += config[10, unc_idx] == duke_idx

# UNC plays Clem in second date
model += config[1, unc_idx] == clem_idx

# Duke has a bye in date 16
model += where[15, duke_idx] == 2

# Wake does not play home in date 17
model += where[16, wake_idx] != 0

# Wake has a bye in first date
model += where[0, wake_idx] == 2

# Clem, Duke, UMD and Wake do not play away in last date
for t in [clem_idx, duke_idx, umd_idx, wake_idx]:
    model += where[n_days-1, t] != 1

# Clem, FSU, GT and Wake do not play away in first date
for t in [clem_idx, fsu_idx, gt_idx, wake_idx]:
    model += where[0, t] != 1

# Neither FSU nor NCSt have a bye in last date
for t in [fsu_idx, ncst_idx]:
    model += where[n_days-1, t] != 2

# UNC does not have a bye in first date
model += where[0, unc_idx] != 2

# Solve
model.solve()

# Print solution
solution = {
    "config": config.value().tolist(),
    "where": where.value().tolist()
}
print(json.dumps(solution))