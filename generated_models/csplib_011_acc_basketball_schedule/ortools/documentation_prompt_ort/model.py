from ortools.sat.python import cp_model
import json

# Input data
n_teams = 9
n_days = 18
teams = ['Clem', 'Duke', 'FSU', 'GT', 'UMD', 'UNC', 'NCSt', 'UVA', 'Wake']

# Map team names to indices for convenience
team_idx = {team: i for i, team in enumerate(teams)}

# Mirroring pairs (1-based to 0-based)
mirroring_pairs = [(0, 7), (1, 8), (2, 11), (3, 12), (4, 13), (5, 14), (6, 15), (9, 16), (10, 17)]

# Rival pairs (team indices)
rivals = {
    team_idx['Duke']: team_idx['UNC'],
    team_idx['Clem']: team_idx['GT'],
    team_idx['NCSt']: team_idx['Wake'],
    team_idx['UMD']: team_idx['UVA'],
}

# Constrained matches in dates 11 to 18 (0-based: 10 to 17)
constrained_pairs = [
    (team_idx['Wake'], team_idx['UNC']),
    (team_idx['Wake'], team_idx['Duke']),
    (team_idx['GT'], team_idx['UNC']),
    (team_idx['GT'], team_idx['Duke']),
]

# Weekend dates (even dates 2,4,...18 are weekends, 0-based: 1,3,...17)
weekend_dates = [d for d in range(n_days) if (d + 1) % 2 == 0]
weekday_dates = [d for d in range(n_days) if (d + 1) % 2 == 1]

model = cp_model.CpModel()

# Decision variables:
# config[d][t]: opponent team index or -1 if bye on day d for team t
# where[d][t]: 0=home, 1=away, 2=bye
config = []
where = []
for d in range(n_days):
    config.append([model.NewIntVar(-1, n_teams - 1, f'config_d{d}_t{t}') for t in range(n_teams)])
    where.append([model.NewIntVar(0, 2, f'where_d{d}_t{t}') for t in range(n_teams)])

# Helper: team plays or not on day d
def plays(d, t):
    # True if not bye
    return model.NewBoolVar(f'plays_d{d}_t{t}')

for d in range(n_days):
    for t in range(n_teams):
        # plays[d][t] = (where[d][t] != 2)
        model.Add(where[d][t] != 2).OnlyEnforceIf(plays(d, t))
        model.Add(where[d][t] == 2).OnlyEnforceIf(plays(d, t).Not())

# 1. Mirroring: For each pair (r1, r2), each team plays same opponent
for (r1, r2) in mirroring_pairs:
    for t in range(n_teams):
        model.Add(config[r1][t] == config[r2][t])
        model.Add(where[r1][t] == where[r2][t])

# 2. No Two Final Aways: no team plays away on both last dates (17 and 18, 0-based 16 and 17)
for t in range(n_teams):
    away_16 = model.NewBoolVar(f'away_16_t{t}')
    away_17 = model.NewBoolVar(f'away_17_t{t}')
    model.Add(where[16][t] == 1).OnlyEnforceIf(away_16)
    model.Add(where[16][t] != 1).OnlyEnforceIf(away_16.Not())
    model.Add(where[17][t] == 1).OnlyEnforceIf(away_17)
    model.Add(where[17][t] != 1).OnlyEnforceIf(away_17.Not())
    model.AddBoolOr([away_16.Not(), away_17.Not()])  # not both away

# 3. Home/Away/Bye Pattern Constraints
# No more than two away matches in a row
for t in range(n_teams):
    for start in range(n_days - 2):
        # sum of where[d][t] == 1 for d in start..start+2 <= 2
        model.Add(sum(where[d][t] == 1 for d in range(start, start + 3)) <= 2)
# No more than two home matches in a row
for t in range(n_teams):
    for start in range(n_days - 2):
        model.Add(sum(where[d][t] == 0 for d in range(start, start + 3)) <= 2)
# No more than three away matches or byes in a row
for t in range(n_teams):
    for start in range(n_days - 3):
        # where[d][t] in {1,2} means away or bye
        model.Add(sum((where[d][t] == 1) + (where[d][t] == 2) for d in range(start, start + 4)) <= 3)
# No more than four home matches or byes in a row
for t in range(n_teams):
    for start in range(n_days - 4):
        # where[d][t] in {0,2} means home or bye
        model.Add(sum((where[d][t] == 0) + (where[d][t] == 2) for d in range(start, start + 5)) <= 4)

# 4. Weekend Pattern: each team plays 4 home, 4 away, 1 bye on weekends
for t in range(n_teams):
    home_count = sum(where[d][t] == 0 for d in weekend_dates)
    away_count = sum(where[d][t] == 1 for d in weekend_dates)
    bye_count = sum(where[d][t] == 2 for d in weekend_dates)
    model.Add(home_count == 4)
    model.Add(away_count == 4)
    model.Add(bye_count == 1)

# 5. First Weekends: each team must have home or bye at least on two of first five weekends
first_five_weekends = [d for d in weekend_dates if d < 10]  # first 5 weekends (dates 2,4,6,8,10)
for t in range(n_teams):
    home_or_bye = [model.NewBoolVar(f'home_or_bye_d{d}_t{t}') for d in first_five_weekends]
    for i, d in enumerate(first_five_weekends):
        model.AddBoolOr([where[d][t] == 0, where[d][t] == 2]).OnlyEnforceIf(home_or_bye[i])
        model.AddBoolAnd([where[d][t] != 0, where[d][t] != 2]).OnlyEnforceIf(home_or_bye[i].Not())
    model.Add(sum(home_or_bye) >= 2)

# 6. Rival Matches: last date (17) every team except FSU plays against rival unless plays FSU or bye
last_date = 17
for t in range(n_teams):
    if t == team_idx['FSU']:
        continue
    if t in rivals:
        rival = rivals[t]
        # If team t plays FSU or bye, no constraint
        plays_fsu = model.NewBoolVar(f'plays_fsu_last_t{t}')
        model.Add(config[last_date][t] == team_idx['FSU']).OnlyEnforceIf(plays_fsu)
        model.Add(config[last_date][t] != team_idx['FSU']).OnlyEnforceIf(plays_fsu.Not())
        bye_last = model.NewBoolVar(f'bye_last_t{t}')
        model.Add(where[last_date][t] == 2).OnlyEnforceIf(bye_last)
        model.Add(where[last_date][t] != 2).OnlyEnforceIf(bye_last.Not())
        # If not plays FSU and not bye, must play rival
        model.Add(config[last_date][t] == rival).OnlyEnforceIf([plays_fsu.Not(), bye_last.Not()])

# 7. Constrained Matches: pairings must occur at least once in dates 11 to 18 (10 to 17)
for (t1, t2) in constrained_pairs:
    occurs = []
    for d in range(10, 18):
        # team t1 plays t2 or t2 plays t1 on day d
        plays_pair = model.NewBoolVar(f'plays_pair_{t1}_{t2}_d{d}')
        model.AddBoolOr([
            config[d][t1] == t2,
            config[d][t2] == t1,
        ]).OnlyEnforceIf(plays_pair)
        model.AddBoolAnd([
            config[d][t1] != t2,
            config[d][t2] != t1,
        ]).OnlyEnforceIf(plays_pair.Not())
        occurs.append(plays_pair)
    model.Add(sum(occurs) >= 1)

# 8. Opponent Sequence Constraints
# No team plays in two consecutive dates away against UNC and Duke
unc = team_idx['UNC']
duke = team_idx['Duke']
for t in range(n_teams):
    for d in range(n_days - 1):
        # away against UNC on d and away against Duke on d+1 not allowed
        cond1 = model.NewBoolVar(f'away_unc_d{d}_t{t}')
        cond2 = model.NewBoolVar(f'away_duke_d{d+1}_t{t}')
        model.Add(config[d][t] == unc).OnlyEnforceIf(cond1)
        model.Add(config[d][t] != unc).OnlyEnforceIf(cond1.Not())
        model.Add(where[d][t] == 1).OnlyEnforceIf(cond1)
        model.Add(where[d][t] != 1).OnlyEnforceIf(cond1.Not())
        model.Add(config[d+1][t] == duke).OnlyEnforceIf(cond2)
        model.Add(config[d+1][t] != duke).OnlyEnforceIf(cond2.Not())
        model.Add(where[d+1][t] == 1).OnlyEnforceIf(cond2)
        model.Add(where[d+1][t] != 1).OnlyEnforceIf(cond2.Not())
        model.AddBoolOr([cond1.Not(), cond2.Not()])

# No team plays in three consecutive dates against UNC, Duke and Wake (any home/away)
wake = team_idx['Wake']
for t in range(n_teams):
    for d in range(n_days - 2):
        conds = []
        conds.append(model.NewBoolVar(f'plays_unc_d{d}_t{t}'))
        conds.append(model.NewBoolVar(f'plays_duke_d{d+1}_t{t}'))
        conds.append(model.NewBoolVar(f'plays_wake_d{d+2}_t{t}'))
        model.AddBoolOr([config[d][t] != unc]).OnlyEnforceIf(conds[0].Not())
        model.Add(config[d][t] == unc).OnlyEnforceIf(conds[0])
        model.AddBoolOr([config[d+1][t] != duke]).OnlyEnforceIf(conds[1].Not())
        model.Add(config[d+1][t] == duke).OnlyEnforceIf(conds[1])
        model.AddBoolOr([config[d+2][t] != wake]).OnlyEnforceIf(conds[2].Not())
        model.Add(config[d+2][t] == wake).OnlyEnforceIf(conds[2])
        model.AddBoolOr([conds[0].Not(), conds[1].Not(), conds[2].Not()])

# 9. Other Constraints
# UNC plays rival Duke in last date and date 11 (0-based 10)
model.Add(config[last_date][unc] == duke)
model.Add(config[10][unc] == duke)
# UNC plays Clem in second date (1-based 2, 0-based 1)
model.Add(config[1][unc] == team_idx['Clem'])
# Duke has a bye in date 16 (0-based 15)
model.Add(where[15][duke] == 2)
model.Add(config[15][duke] == -1)
# Wake does not play home in date 17 (0-based 16)
model.Add(where[16][team_idx['Wake']] != 0)
# Wake has a bye in first date (0-based 0)
model.Add(where[0][team_idx['Wake']] == 2)
model.Add(config[0][team_idx['Wake']] == -1)
# Clem, Duke, UMD and Wake do not play away in last date (17)
for t in [team_idx['Clem'], team_idx['Duke'], team_idx['UMD'], team_idx['Wake']]:
    model.Add(where[last_date][t] != 1)
# Clem, FSU, GT and Wake do not play away in first date (0)
for t in [team_idx['Clem'], team_idx['FSU'], team_idx['GT'], team_idx['Wake']]:
    model.Add(where[0][t] != 1)
# Neither FSU nor NCSt have a bye in last date (17)
for t in [team_idx['FSU'], team_idx['NCSt']]:
    model.Add(where[last_date][t] != 2)
# UNC does not have a bye in first date (0)
model.Add(where[0][unc] != 2)

# Additional constraints to ensure consistency of config and where:
# If config[d][t] == -1 then where[d][t] ==