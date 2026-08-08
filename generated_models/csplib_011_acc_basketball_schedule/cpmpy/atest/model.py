# Import libraries
from cpmpy import *
import json

# Parameters
n_teams = 9  # Number of teams
n_days = 18  # Number of days
n_matches_per_day = 4  # Number of matches per day (9 teams, 18 days, 4 matches per day)

# Teams
teams = ["Clem", "Duke", "FSU", "GT", "UMD", "UNC", "NCSt", "UVA", "Wake"]

# Mirroring scheme
mirroring = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]

# Rival pairs
rival_pairs = [("Duke", "UNC"), ("Clem", "GT"), ("NCSt", "Wake"), ("UMD", "UVA")]

# Constrained matches
constrained_matches = [("Wake", "UNC"), ("Wake", "Duke"), ("GT", "UNC"), ("GT", "Duke")]

# Decision variables
# config[i][j] = (home_team, away_team) for match j on day i
config = intvar(0, n_teams - 1, shape=(n_days, n_matches_per_day, 2), name="config")

# where[i][j][k] = 0 if team k is home in match j on day i, 1 if away, 2 if bye
where = intvar(0, 2, shape=(n_days, n_matches_per_day, n_teams), name="where")

# Model
model = Model()

# Constraint 1: Each team plays each other team twice (once at home, once away)
for i in range(n_teams):
    for j in range(i + 1, n_teams):
        # Count how many times team i plays team j at home
        home_count = sum((config[:, :, 0] == i) & (config[:, :, 1] == j))
        # Count how many times team i plays team j away
        away_count = sum((config[:, :, 0] == j) & (config[:, :, 1] == i))
        # Each pair must play twice (once at home, once away)
        model += [home_count == 1, away_count == 1]

# Constraint 2: No Two Final Aways
# No team can play away on both last dates
for t in range(n_teams):
    model += [sum(where[n_days - 1, :, t] == 1) <= 1]

# Constraint 3: Home/Away/Bye Pattern Constraints
# No team may have more than two away matches in a row
# No team may have more than two home matches in a row
# No team may have more than three away matches or byes in a row
# No team may have more than four home matches or byes in a row
for t in range(n_teams):
    for d in range(n_days - 2):
        # No more than two away matches in a row
        model += [sum(where[d:d + 3, :, t] == 1) <= 2]
        # No more than two home matches in a row
        model += [sum(where[d:d + 3, :, t] == 0) <= 2]
        # No more than three away matches or byes in a row
        model += [sum((where[d:d + 3, :, t] == 1) | (where[d:d + 3, :, t] == 2)) <= 3]
        # No more than four home matches or byes in a row
        model += [sum((where[d:d + 4, :, t] == 0) | (where[d:d + 4, :, t] == 2)) <= 4]

# Constraint 4: Weekend Pattern
# Of the weekends, each team plays four at home, four away, and one bye
# Even days are weekends
weekends = [d for d in range(n_days) if d % 2 == 1]
for t in range(n_teams):
    home_weekends = sum(where[weekends, :, t] == 0)
    away_weekends = sum(where[weekends, :, t] == 1)
    bye_weekends = sum(where[weekends, :, t] == 2)
    model += [home_weekends == 4, away_weekends == 4, bye_weekends == 1]

# Constraint 5: First Weekends
# Each team must have home matches or byes at least on two of the first five weekends
first_five_weekends = [d for d in range(n_days) if d % 2 == 1 and d < 10]
for t in range(n_teams):
    home_or_bye_first_five_weekends = sum((where[first_five_weekends, :, t] == 0) | (where[first_five_weekends, :, t] == 2))
    model += [home_or_bye_first_five_weekends >= 2]

# Constraint 6: Rival Matches
# Every team except FSU has a traditional rival. The rival pairs are Duke-UNC, Clem-GT, NCSt-Wake, and UMD-UVA.
# In the last date, every team except FSU plays against its rival, unless it plays against FSU or has a bye.
for t in range(n_teams):
    if teams[t] != "FSU":
        rival = None
        if teams[t] == "Duke":
            rival = "UNC"
        elif teams[t] == "UNC":
            rival = "Duke"
        elif teams[t] == "Clem":
            rival = "GT"
        elif teams[t] == "GT":
            rival = "Clem"
        elif teams[t] == "NCSt":
            rival = "Wake"
        elif teams[t] == "Wake":
            rival = "NCSt"
        elif teams[t] == "UMD":
            rival = "UVA"
        elif teams[t] == "UVA":
            rival = "UMD"
        # Get the index of the rival team
        rival_index = teams.index(rival)
        # On the last date, team t plays against its rival unless it plays against FSU or has a bye
        model += [((config[n_days - 1, :, 0] == t) & (config[n_days - 1, :, 1] == rival_index)) |
                  ((config[n_days - 1, :, 0] == rival_index) & (config[n_days - 1, :, 1] == t)) |
                  ((config[n_days - 1, :, 0] == t) & (config[n_days - 1, :, 1] == teams.index("FSU"))) |
                  ((config[n_days - 1, :, 0] == teams.index("FSU")) & (config[n_days - 1, :, 1] == t)) |
                  (where[n_days - 1, :, t] == 2)]

# Constraint 7: Constrained Matches
# The following pairings must occur at least once in dates 11 to 18: Wake-UNC, Wake-Duke, GT-UNC, and GT-Duke.
constrained_dates = [10, 11, 12, 13, 14, 15, 16, 17]  # 0-indexed
for pair in constrained_matches:
    team1 = teams.index(pair[0])
    team2 = teams.index(pair[1])
    # Count how many times the pair plays in constrained dates
    count = sum(((config[constrained_dates, :, 0] == team1) & (config[constrained_dates, :, 1] == team2)) |
                ((config[constrained_dates, :, 0] == team2) & (config[constrained_dates, :, 1] == team1)))
    model += [count >= 1]

# Constraint 8: Opponent Sequence Constraints
# No team plays in two consecutive dates away against UNC and Duke.
# No team plays in three consecutive dates against UNC, Duke and Wake (independent of home/away).
for t in range(n_teams):
    for d in range(n_days - 1):
        # No team plays in two consecutive dates away against UNC and Duke
        model += [((config[d, :, 1] == teams.index("UNC")) & (config[d + 1, :, 1] == teams.index("Duke"))) |
                  ((config[d, :, 1] == teams.index("Duke")) & (config[d + 1, :, 1] == teams.index("UNC"))) |
                  ((config[d, :, 0] == t) & (config[d + 1, :, 0] == t))]
    for d in range(n_days - 2):
        # No team plays in three consecutive dates against UNC, Duke and Wake (independent of home/away)
        model += [((config[d, :, 0] == teams.index("UNC")) | (config[d, :, 1] == teams.index("UNC"))) &
                  ((config[d + 1, :, 0] == teams.index("Duke")) | (config[d + 1, :, 1] == teams.index("Duke"))) &
                  ((config[d + 2, :, 0] == teams.index("Wake")) | (config[d + 2, :, 1] == teams.index("Wake"))) |
                  ((config[d, :, 0] == teams.index("Duke")) | (config[d, :, 1] == teams.index("Duke"))) &
                  ((config[d + 1, :, 0] == teams.index("UNC")) | (config[d + 1, :, 1] == teams.index("UNC"))) &
                  ((config[d + 2, :, 0] == teams.index("Wake")) | (config[d + 2, :, 1] == teams.index("Wake"))) |
                  ((config[d, :, 0] == teams.index("UNC")) | (config[d, :, 1] == teams.index("UNC"))) &
                  ((config[d + 1, :, 0] == teams.index("Wake")) | (config[d + 1, :, 1] == teams.index("Wake"))) &
                  ((config[d + 2, :, 0] == teams.index("Duke")) | (config[d + 2, :, 1] == teams.index("Duke"))) |
                  ((config[d, :, 0] == teams.index("Duke")) | (config[d, :, 1] == teams.index("Duke"))) &
                  ((config[d + 1, :, 0] == teams.index("Wake")) | (config[d + 1, :, 1] == teams.index("Wake"))) &
                  ((config[d + 2, :, 0] == teams.index("UNC")) | (config[d + 2, :, 1] == teams.index("UNC")))]

# Constraint 9: Other Constraints
# UNC plays its rival Duke in the last date and in date 11.
# UNC plays Clem in the second date.
# Duke has a bye in date 16.
# Wake does not play home in date 17.
# Wake has a bye in the first date.
# Clem, Duke, UMD and Wake do not play away in the last date.
# Clem, FSU, GT and Wake do not play away in the first date.
# Neither FSU nor NCSt have a bye in the last date.
# UNC does not have a bye in the first date.

# UNC plays its rival Duke in the last date and in date 11
unc_index = teams.index("UNC")
duke_index = teams.index("Duke")
clem_index = teams.index("Clem")
fsu_index = teams.index("FSU")
gt_index = teams.index("GT")
umd_index = teams.index("UMD")
ncst_index = teams.index("NCSt")
uva_index = teams.index("UVA")
wake_index = teams.index("Wake")

# UNC plays Duke in the last date
model += [(config[n_days - 1, :, 0] == unc_index) & (config[n_days - 1, :, 1] == duke_index) |
          (config[n_days - 1, :, 0] == duke_index) & (config[n_days - 1, :, 1] == unc_index)]

# UNC plays Duke in date 11
model += [(config[10, :, 0] == unc_index) & (config[10, :, 1] == duke_index) |
          (config[10, :, 0] == duke_index) & (config[10, :, 1] == unc_index)]

# UNC plays Clem in the second date
model += [(config[1, :, 0] == unc_index) & (config[1, :, 1] == clem_index) |
          (config[1, :, 0] == clem_index) & (config[1, :, 1] == unc_index)]

# Duke has a bye in date 16
model += [where[15, :, duke_index] == 2]

# Wake does not play home in date 17
model += [where[16, :, wake_index] != 0]

# Wake has a bye in the first date
model += [where[0, :, wake_index] == 2]

# Clem, Duke, UMD and Wake do not play away in the last date
model += [where[n_days - 1, :, clem_index] != 1]
model += [where[n_days - 1, :, duke_index] != 1]
model += [where[n_days - 1, :, umd_index] != 1]
model += [where[n_days - 1, :, wake_index] != 1]

# Clem, FSU, GT and Wake do not play away in the first date
model += [where[0, :, clem_index] != 1]
model += [where[0, :, fsu_index] != 1]
model += [where[0, :, gt_index] != 1]
model += [where[0, :, wake_index] != 1]

# Neither FSU nor NCSt have a bye in the last date
model += [where[n_days - 1, :, fsu_index] != 2]
model += [where[n_days - 1, :, ncst_index] != 2]

# UNC does not have a bye in the first date
model += [where[0, :, unc_index] != 2]

# Solve
model.solve()

# Print the solution
solution = {
    "config": config.value().tolist(),
    "where": where.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script