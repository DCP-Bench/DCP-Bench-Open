
import cpmpy as cp
import json

# Data
n_teams = 9
n_days = 18

# Team indices (for clarity in constraints)
# 0:Clem,1:Duke,2:FSU,3:GT,4:UMD,5:UNC,6:NCSt,7:UVA,8:Wake

# Model definition
model = cp.Model()

# Decision Variables
# config[d,i] = j means team i plays team j on day d. A bye is represented by config[d,i] == i
config = cp.intvar(0, n_teams - 1, shape=(n_days, n_teams), name="config")

# where[d,i] in {-1,0,2}: -1 = bye, 0 = home, 2 = away
where = cp.intvar(-1, 2, shape=(n_days, n_teams), name="where")

# Boolean indicators for clarity and linking
is_bye = cp.boolvar(shape=(n_days, n_teams), name="is_bye")
is_home = cp.boolvar(shape=(n_days, n_teams), name="is_home")
is_away = cp.boolvar(shape=(n_days, n_teams), name="is_away")

# Constraints

# Exactly one of bye/home/away per (day,team) and link where variable
for d in range(n_days):
    for t in range(n_teams):
        model += (is_bye[d, t] + is_home[d, t] + is_away[d, t] == 1)
        # where = -1*is_bye + 2*is_away (is_home contributes 0)
        model += (where[d, t] == -1 * is_bye[d, t] + 2 * is_away[d, t])
        # bye implies self in config; non-bye implies not self
        model += is_bye[d, t].implies(config[d, t] == t)
        model += (~is_bye[d, t]).implies(config[d, t] != t)

# Each day exactly one bye (odd number of teams)
for d in range(n_days):
    model += (cp.sum(is_bye[d, :]) == 1)

# Matches are symmetric and home/away complementary
for d in range(n_days):
    for i in range(n_teams):
        for j in range(n_teams):
            if i == j:
                continue
            # If i is scheduled to play j on day d then j plays i
            model += (config[d, i] == j).implies(config[d, j] == i)
            # If i plays j then neither is a bye
            model += (config[d, i] == j).implies(~is_bye[d, i])
            model += (config[d, i] == j).implies(~is_bye[d, j])
            # If i plays j then home/away sum to 2 (one home (0) + one away (2) = 2)
            model += (config[d, i] == j).implies(where[d, i] + where[d, j] == 2)

# Each pair of distinct teams meet exactly twice (double round-robin)
for i in range(n_teams):
    for j in range(i+1, n_teams):
        model += cp.sum([(config[d, i] == j) for d in range(n_days)]) == 2

# Each team has exactly 2 byes (18 dates, 16 matches)
for t in range(n_teams):
    model += cp.sum([is_bye[d, t] for d in range(n_days)]) == 2

# Each team has 8 home and 8 away matches (16 games)
for t in range(n_teams):
    model += cp.sum([is_home[d, t] for d in range(n_days)]) == 8
    model += cp.sum([is_away[d, t] for d in range(n_days)]) == 8

# Mirroring scheme (given, converted to 0-based indices)
mirror_pairs = [(0,7),(1,8),(2,11),(3,12),(4,13),(5,14),(6,15),(9,16),(10,17)]
for (r1, r2) in mirror_pairs:
    for t in range(n_teams):
        # same opponent in mirrored dates
        model += (config[r1, t] == config[r2, t])
        # if not a bye in those dates, home/away swapped (sum == 2)
        model += (~is_bye[r1, t]).implies(where[r1, t] + where[r2, t] == 2)
        # if bye on r1 then bye also on r2 (since config equal and config==t implies bye)
        model += is_bye[r1, t].implies(is_bye[r2, t])
        model += is_bye[r2, t].implies(is_bye[r1, t])

# No Two Final Aways: no team can play away on both of the last two dates (dates 17 and 18 -> indices 16,17)
for t in range(n_teams):
    model += (is_away[16, t] + is_away[17, t] <= 1)

# Home/Away/Bye Pattern Constraints
# No more than two away matches in a row (i.e., no run of 3 all away)
for t in range(n_teams):
    for d in range(n_days - 2):
        model += (is_away[d, t] + is_away[d+1, t] + is_away[d+2, t] <= 2)
# No more than two home matches in a row
for t in range(n_teams):
    for d in range(n_days - 2):
        model += (is_home[d, t] + is_home[d+1, t] + is_home[d+2, t] <= 2)
# No more than three away matches or byes in a row (window 4)
for t in range(n_teams):
    for d in range(n_days - 3):
        model += ( (is_away[d, t] + is_bye[d, t]) + (is_away[d+1, t] + is_bye[d+1, t]) +
                   (is_away[d+2, t] + is_bye[d+2, t]) + (is_away[d+3, t] + is_bye[d+3, t]) <= 3 )
# No more than four home matches or byes in a row (window 5)
for t in range(n_teams):
    for d in range(n_days - 4):
        model += ( (is_home[d, t] + is_bye[d, t]) + (is_home[d+1, t] + is_bye[d+1, t]) +
                   (is_home[d+2, t] + is_bye[d+2, t]) + (is_home[d+3, t] + is_bye[d+3, t]) +
                   (is_home[d+4, t] + is_bye[d+4, t]) <= 4 )

# Weekend pattern: weekends are even dates (2,4,...,18) -> zero-based indices 1,3,...,17
weekend_days = [d for d in range(n_days) if (d % 2) == 1]  # 1,3,5,...,17
for t in range(n_teams):
    model += cp.sum([is_home[d, t] for d in weekend_days]) == 4
    model += cp.sum([is_away[d, t] for d in weekend_days]) == 4
    model += cp.sum([is_bye[d, t] for d in weekend_days]) == 1

# First Weekends: first five weekends are the first five weekend days (indices 1,3,5,7,9)
first_five_weekends = weekend_days[:5]
for t in range(n_teams):
    # home matches or byes at least on two of these weekends
    model += cp.sum([is_home[d, t] + is_bye[d, t] for d in first_five_weekends]) >= 2

# Rival Matches: rivals map (except FSU which has none)
rivals = {1:5, 5:1, 0:3, 3:0, 6:8, 8:6, 4:7, 7:4}  # symmetric
# In the last date (index 17), every team except FSU (2) plays their rival unless they play FSU or have a bye.
for t, r in rivals.items():
    # allow rival OR playing FSU OR bye
    model += ( (config[17, t] == r) | (config[17, t] == 2) | (is_bye[17, t]) )

# Constrained Matches: the following pairings must occur at least once in dates 11..18 (indices 10..17)
required_pairs = [(8,5), (8,1), (3,5), (3,1)]  # (Wake-UNC), (Wake-Duke), (GT-UNC), (GT-Duke)
for (i,j) in required_pairs:
    model += cp.sum([ (config[d, i] == j) for d in range(10, 18) ]) >= 1

# Opponent Sequence Constraints
# No team plays in two consecutive dates away against UNC(5) and Duke(1) (in either order).
for t in range(n_teams):
    for d in range(n_days - 1):
        # forbid UNC away then Duke away
        model += ~( (config[d, t] == 5) & (is_away[d, t]) & (config[d+1, t] == 1) & (is_away[d+1, t]) )
        # forbid Duke away then UNC away
        model += ~( (config[d, t] == 1) & (is_away[d, t]) & (config[d+1, t] == 5) & (is_away[d+1, t]) )

# No team plays in three consecutive dates against UNC(5), Duke(1), and Wake(8) (any order, home/away irrelevant).
special_set = {1,5,8}
for t in range(n_teams):
    for d in range(n_days - 2):
        model += ~( (config[d, t] .isin(list(special_set))) &
                    (config[d+1, t] .isin(list(special_set))) &
                    (config[d+2, t] .isin(list(special_set))) )

# Other specific constraints (as listed)
# UNC plays its rival Duke in the last date, and in date 11 (indices 17 and 10)
model += (config[17, 5] == 1)
model += (config[10, 5] == 1)
# UNC plays Clem in the second date (index 1)
model += (config[1, 5] == 0)
# Duke has a bye in date 16 (index 15)
model += is_bye[15, 1]
model += (config[15, 1] == 1)
# Wake does not play home in date 17 (index 16)
model += (is_home[16, 8] == 0)
# Wake has a bye in the first date (index 0)
model += is_bye[0, 8]
model += (config[0, 8] == 8)
# Clem, Duke, UMD and Wake do not play away in the last date (index 17)
for t in [0, 1, 4, 8]:
    model += (is_away[17, t] == 0)
# Clem, FSU, GT and Wake do not play away in the first date (index 0)
for t in [0, 2, 3, 8]:
    model += (is_away[0, t] == 0)
# Neither FSU nor NCSt have a bye in the last date (index 17)
for t in [2, 6]:
    model += (is_bye[17, t] == 0)
# UNC does not have a bye in the first date (index 0)
model += (is_bye[0, 5] == 0)

# Solve the model
if model.solve():
    # Prepare outputs: config as list of lists, where as list of lists
    config_sol = config.value().tolist()
    where_sol = where.value().tolist()
    # Ensure integers (they already are), but cast inner elements explicitly
    config_sol = [[int(x) for x in row] for row in config_sol]
    where_sol = [[int(x) for x in row] for row in where_sol]
    solution = {'config': config_sol, 'where': where_sol}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
