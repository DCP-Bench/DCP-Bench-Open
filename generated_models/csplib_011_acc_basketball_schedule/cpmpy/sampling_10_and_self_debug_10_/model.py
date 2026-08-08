
import cpmpy as cp
import json

# Data
n_teams = 9
n_days = 18

# Team indexing (0-based)
teams = ["Clem", "Duke", "FSU", "GT", "UMD", "UNC", "NCSt", "UVA", "Wake"]
idx = {teams[i]: i for i in range(n_teams)}

# Mirroring scheme given (1-based in problem), convert to 0-based
mirrors_1based = [(1,8), (2,9), (3,12), (4,13), (5,14), (6,15), (7,16), (10,17), (11,18)]
mirrors = [(a-1, b-1) for (a, b) in mirrors_1based]

# Weekend days (1-based even dates are weekends -> 0-based odd indices)
weekends = [d for d in range(n_days) if d % 2 == 1]
first_five_weekends = weekends[:5]  # first five weekend dates

# Model
model = cp.Model()

# Decision variables
# config[d,i] = opponent team index 0..8 or -1 for bye
config = cp.intvar(-1, n_teams-1, shape=(n_days, n_teams), name="config")

# where[d,i] = -1 for bye, 0 for home, 2 for away
where = cp.intvar(-1, 2, shape=(n_days, n_teams), name="where")

# Restrict where to values in {-1,0,2}
for d in range(n_days):
    for t in range(n_teams):
        model += cp.InDomain(where[d, t], [-1, 0, 2])

# Basic consistency constraints

# 1) No self-play
for d in range(n_days):
    for i in range(n_teams):
        model += (config[d, i] != i)

# 2) Symmetry: if i plays j on day d then j plays i on day d
for d in range(n_days):
    for i in range(n_teams):
        for j in range(n_teams):
            if i != j:
                model += (config[d, i] == j).implies(config[d, j] == i)

# 3) If team has a bye, where must be -1; if config != -1 then where cannot be -1 (i.e., playing implies not bye)
for d in range(n_days):
    for i in range(n_teams):
        model += (config[d, i] == -1).implies(where[d, i] == -1)
        model += (where[d, i] != -1).implies(config[d, i] != -1)

# 4) For any scheduled match (i vs j) on day d, their where values must be complementary (0 vs 2)
for d in range(n_days):
    for i in range(n_teams):
        for j in range(n_teams):
            if i != j:
                # if i plays j, then where[i] + where[j] == 2 (0 + 2)
                model += (config[d, i] == j).implies(where[d, i] + where[d, j] == 2)

# 5) Each day exactly one bye (since odd number of teams)
for d in range(n_days):
    model += cp.sum([config[d, i] == -1 for i in range(n_teams)]) == 1

# 6) Each team has exactly 2 byes over the season (18 days, double round robin => 16 games + 2 byes)
for i in range(n_teams):
    model += cp.sum([config[d, i] == -1 for d in range(n_days)]) == 2

# 7) Double round-robin: each pair plays twice (once each home)
for i in range(n_teams):
    for j in range(i+1, n_teams):
        # They must meet exactly twice across the season
        model += cp.sum([config[d, i] == j for d in range(n_days)]) == 2
        # And each team hosts the other exactly once
        model += cp.sum([(config[d, i] == j) & (where[d, i] == 0) for d in range(n_days)]) == 1

# Mirroring constraint: for each mirror pair, opponents are the same and home/away are swapped (when not bye)
for (r1, r2) in mirrors:
    for i in range(n_teams):
        model += (config[r1, i] == config[r2, i])
        # If it's not a bye, the where values should be complementary (0+2)
        model += (config[r1, i] != -1).implies(where[r1, i] + where[r2, i] == 2)
        # If it's a bye on r1 then where r1 must be -1 (already enforced globally), and equality of config implies bye on r2 too

# Constraint 2: No team away on both last dates (last two days)
last1 = n_days - 2
last2 = n_days - 1
for i in range(n_teams):
    model += cp.sum([(where[last1, i] == 2), (where[last2, i] == 2)]) <= 1

# Constraint 3: Home/Away/Bye pattern constraints
# No more than two away in a row -> any window of length 3: away-count <= 2
for i in range(n_teams):
    for start in range(n_days - 3 + 1):
        model += cp.sum([(where[start + k, i] == 2) for k in range(3)]) <= 2

# No more than two home in a row -> any window of length 3: home-count <= 2
for i in range(n_teams):
    for start in range(n_days - 3 + 1):
        model += cp.sum([(where[start + k, i] == 0) for k in range(3)]) <= 2

# No more than three away or byes in a row -> any window of length 4: (away or bye) count <= 3
for i in range(n_teams):
    for start in range(n_days - 4 + 1):
        model += cp.sum([((where[start + k, i] == 2) | (where[start + k, i] == -1)) for k in range(4)]) <= 3

# No more than four home or byes in a row -> any window of length 5: (home or bye) count <=4
for i in range(n_teams):
    for start in range(n_days - 5 + 1):
        model += cp.sum([((where[start + k, i] == 0) | (where[start + k, i] == -1)) for k in range(5)]) <= 4

# Constraint 4: Weekend pattern - on weekends each team: 4 home, 4 away, 1 bye
for i in range(n_teams):
    model += cp.sum([(where[d, i] == 0) for d in weekends]) == 4
    model += cp.sum([(where[d, i] == 2) for d in weekends]) == 4
    model += cp.sum([(where[d, i] == -1) for d in weekends]) == 1

# Constraint 5: First five weekends: each team must have home or bye on at least two of these weekends
for i in range(n_teams):
    model += cp.sum([((where[d, i] == 0) | (where[d, i] == -1)) for d in first_five_weekends]) >= 2

# Constraint 6: Rival matches on last date except FSU (unless playing FSU or bye)
rivals = {
    idx["Duke"]: idx["UNC"],
    idx["Clem"]: idx["GT"],
    idx["NCSt"]: idx["Wake"],
    idx["UMD"]: idx["UVA"],
    # UNC is covered as Duke-UNC pair via symmetric relation already; we ensure both sides by checking each team with its rival
}
# For teams with rivals, except FSU (index 2)
for t, r in rivals.items():
    # if not playing FSU and not bye, must play rival on last day
    model += ((config[last2, t] != idx["FSU"]) & (config[last2, t] != -1)).implies(config[last2, t] == r)

# Constraint 7: Constrained matches must occur at least once in dates 11 to 18 (0-based 10..17)
req_pairs = [(idx["Wake"], idx["UNC"]), (idx["Wake"], idx["Duke"]), (idx["GT"], idx["UNC"]), (idx["GT"], idx["Duke"])]
for (a, b) in req_pairs:
    model += cp.sum([(config[d, a] == b) for d in range(10, 18)]) >= 1

# Constraint 8: Opponent sequence constraints
# (a) No team plays in two consecutive dates away against UNC and Duke
target_set = {idx["UNC"], idx["Duke"]}
for i in range(n_teams):
    for d in range(n_days - 1):
        model += cp.sum([((config[d, i] == opp) & (where[d, i] == 2)) for opp in target_set] + \
                        [((config[d+1, i] == opp) & (where[d+1, i] == 2)) for opp in target_set]) <= 1

# (b) No team plays in three consecutive dates against UNC, Duke and Wake (independent of home/away)
target_set3 = {idx["UNC"], idx["Duke"], idx["Wake"]}
for i in range(n_teams):
    for d in range(n_days - 2):
        model += cp.sum([ (config[d + k, i] == opp) for k in range(3) for opp in target_set3 ]) <= 2

# Constraint 9: Other specific constraints
# UNC plays Duke in last date and in date 11 (0-based 10 and 17)
model += config[17, idx["UNC"]] == idx["Duke"]
model += config[10, idx["UNC"]] == idx["Duke"]

# UNC plays Clem in the second date (date 2 -> index 1)
model += config[1, idx["UNC"]] == idx["Clem"]

# Duke has a bye in date 16 (0-based 15)
model += config[15, idx["Duke"]] == -1
model += where[15, idx["Duke"]] == -1

# Wake does not play home in date 17 (0-based 16)
model += (where[16, idx["Wake"]] != 0)

# Wake has a bye in the first date (date 1 -> index 0)
model += config[0, idx["Wake"]] == -1
model += where[0, idx["Wake"]] == -1

# Clem, Duke, UMD and Wake do not play away in the last date
for name in ["Clem", "Duke", "UMD", "Wake"]:
    model += (where[17, idx[name]] != 2)

# Clem, FSU, GT and Wake do not play away in the first date
for name in ["Clem", "FSU", "GT", "Wake"]:
    model += (where[0, idx[name]] != 2)

# Neither FSU nor NCSt have a bye in the last date
for name in ["FSU", "NCSt"]:
    model += (config[17, idx[name]] != -1)

# UNC does not have a bye in the first date
model += (config[0, idx["UNC"]] != -1)

# Solve
if model.solve():
    solution = {
        'config': config.value().tolist(),
        'where': where.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
