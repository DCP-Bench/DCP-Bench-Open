
import cpmpy as cp
import json
import numpy as np

# Data
n_teams = 9
n_days = 18
teams = ["Clem", "Duke", "FSU", "GT", "UMD", "UNC", "NCSt", "UVA", "Wake"]

# Mirroring scheme pairs (1-based to 0-based)
mirroring_pairs = [(0,7), (1,8), (2,11), (3,12), (4,13), (5,14), (6,15), (9,16), (10,17)]

# Rival pairs (team indices)
rivals = {
    1: 5,  # Duke - UNC
    0: 3,  # Clem - GT
    6: 8,  # NCSt - Wake
    4: 7   # UMD - UVA
}
# FSU (2) has no rival

# Weekend dates (0-based even dates)
weekends = [d for d in range(n_days) if (d+1) % 2 == 0]

# Weekday dates (0-based odd dates)
weekdays = [d for d in range(n_days) if (d+1) % 2 == 1]

# Model definition
model = cp.Model()

# Decision variables
# config[d,t]: opponent team index or -1 if bye
config = cp.intvar(-1, n_teams-1, shape=(n_days, n_teams), name="config")
# where[d,t]: 0=bye, 1=home, 2=away
where = cp.intvar(0, 2, shape=(n_days, n_teams), name="where")

# 1) Each team plays each other twice: once home once away
for i in range(n_teams):
    for j in range(i+1, n_teams):
        count_i_home_j_away = cp.sum([(config[d,i] == j) & (where[d,i] == 1) & (where[d,j] == 2) for d in range(n_days)])
        count_j_home_i_away = cp.sum([(config[d,j] == i) & (where[d,j] == 1) & (where[d,i] == 2) for d in range(n_days)])
        model += (count_i_home_j_away == 1)
        model += (count_j_home_i_away == 1)

# 2) Consistency between config and where
for d in range(n_days):
    for t in range(n_teams):
        model += (config[d,t] == -1).implies(where[d,t] == 0)
        model += (config[d,t] != -1).implies((where[d,t] == 1) | (where[d,t] == 2))

# 3) Opponent consistency
for d in range(n_days):
    for t in range(n_teams):
        opp = config[d,t]
        # If opp == -1 (bye), no constraint
        # Else config[d, opp] == t
        model += cp.IfThenElse(
            opp == -1,
            True,
            cp.Element(config[d], opp) == t
        )
        # Home/away consistency:
        model += cp.IfThenElse(
            opp == -1,
            True,
            (where[d,t] == 1).implies(where[d, opp] == 2)
        )
        model += cp.IfThenElse(
            opp == -1,
            True,
            (where[d,t] == 2).implies(where[d, opp] == 1)
        )

# 4) No self-play
for d in range(n_days):
    for t in range(n_teams):
        model += (config[d,t] != t)

# 5) Mirroring scheme
for (r1, r2) in mirroring_pairs:
    for t in range(n_teams):
        model += (config[r1,t] == config[r2,t])
        model += ((where[r1,t] == 1) == (where[r2,t] == 2))

# 6) No two final aways (last two dates: days 16 and 17 zero-based)
for t in range(n_teams):
    model += ~((where[16,t] == 2) & (where[17,t] == 2))

# 7) Home/Away/Bye pattern constraints
for t in range(n_teams):
    # No more than two away matches in a row
    for start in range(n_days-2):
        model += cp.sum([(where[start+i,t] == 2) for i in range(3)]) <= 2
    # No more than two home matches in a row
    for start in range(n_days-2):
        model += cp.sum([(where[start+i,t] == 1) for i in range(3)]) <= 2
    # No more than three away or byes in a row
    for start in range(n_days-3):
        model += cp.sum([(where[start+i,t] == 2) | (where[start+i,t] == 0) for i in range(4)]) <= 3
    # No more than four home or byes in a row
    for start in range(n_days-4):
        model += cp.sum([(where[start+i,t] == 1) | (where[start+i,t] == 0) for i in range(5)]) <= 4

# 8) Weekend pattern: each team plays 4 home, 4 away, 1 bye on weekends
for t in range(n_teams):
    model += cp.sum([where[d,t] == 1 for d in weekends]) == 4
    model += cp.sum([where[d,t] == 2 for d in weekends]) == 4
    model += cp.sum([where[d,t] == 0 for d in weekends]) == 1

# 9) First weekends: each team must have home or bye at least on two of the first five weekends
first_five_weekends = [d for d in weekends if d < 10]  # first 5 weekends (dates 2,4,6,8,10 zero-based: 1,3,5,7,9 one-based)
for t in range(n_teams):
    model += cp.sum([(where[d,t] == 1) | (where[d,t] == 0) for d in first_five_weekends]) >= 2

# 10) Rival matches on last date (day 17 zero-based)
last_day = 17
for t in range(n_teams):
    if t == 2:  # FSU has no rival
        continue
    r = rivals[t]
    # Team t plays rival r on last date, unless plays FSU or has bye
    # So if config[last_day,t] != 2 and config[last_day,t] != -1 then config[last_day,t] == r
    # Equivalently: if config[last_day,t] != 2 and config[last_day,t] != -1 then config[last_day,t] == r
    # So config[last_day,t] in {r, 2, -1}
    model += (config[last_day,t] == r) | (config[last_day,t] == 2) | (config[last_day,t] == -1)

# 11) Constrained matches: Wake-UNC, Wake-Duke, GT-UNC, GT-Duke at least once in dates 10-17 (11-18 one-based)
constrained_pairs = [(8,5), (8,1), (3,5), (3,1)]  # zero-based team indices
for (a,b) in constrained_pairs:
    # At least one date d in 10..17 where a plays b or b plays a
    model += cp.sum([( (config[d,a] == b) | (config[d,b] == a) ) for d in range(10,18)]) >= 1

# 12) Opponent sequence constraints
# No team plays in two consecutive dates away against UNC (5) and Duke (1)
for t in range(n_teams):
    for d in range(n_days-1):
        cond1 = (config[d,t] == 5) & (where[d,t] == 2)
        cond2 = (config[d+1,t] == 1) & (where[d+1,t] == 2)
        model += ~(cond1 & cond2)
        cond3 = (config[d,t] == 1) & (where[d,t] == 2)
        cond4 = (config[d+1,t] == 5) & (where[d+1,t] == 2)
        model += ~(cond3 & cond4)
# No team plays in three consecutive dates against UNC (5), Duke (1), and Wake (8) (home/away doesn't matter)
for t in range(n_teams):
    for d in range(n_days-2):
        conds = [
            (config[d,t] == 5) | (config[d,t] == 1) | (config[d,t] == 8),
            (config[d+1,t] == 5) | (config[d+1,t] == 1) | (config[d+1,t] == 8),
            (config[d+2,t] == 5) | (config[d+2,t] == 1) | (config[d+2,t] == 8)
        ]
        model += ~(conds[0] & conds[1] & conds[2])

# 13) Other constraints
# UNC plays rival Duke in last date and in date 10 (11 one-based)
model += (config[17,5] == 1)  # last date UNC(5) plays Duke(1)
model += (config[10,5] == 1)  # date 11 UNC(5) plays Duke(1)

# UNC plays Clem in second date (date 1 zero-based)
model += (config[1,5] == 0)  # UNC(5) plays Clem(0)

# Duke has a bye in date 15 (16 one-based)
model += (config[15,1] == -1)

# Wake does not play home in date 16 (17 one-based)
model += (where[16,8] != 1)

# Wake has a bye in first date (0 zero-based)
model += (config[0,8] == -1)

# Clem, Duke, UMD and Wake do not play away in last date (17 zero-based)
for t in [0,1,4,8]:
    model += (where[17,t] != 2)

# Clem, FSU, GT and Wake do not play away in first date (0 zero-based)
for t in [0,2,3,8]:
    model += (where[0,t] != 2)

# Neither FSU nor NCSt have a bye in last date (17 zero-based)
for t in [2,6]:
    model += (config[17,t] != -1)

# UNC does not have a bye in first date (0 zero-based)
model += (config[0,5] != -1)

# Solve and print
if model.solve():
    solution = {
        'config': config.value().tolist(),
        'where': where.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
