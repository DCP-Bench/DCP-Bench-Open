from pycsp3 import *

# Sports tournament: n teams play over n-1 weeks. Each week is split into n/2 periods,
# and each period has one match, with a home team and an away team.

n = data.n_teams
n_weeks = n - 1
n_periods = n // 2

# home[w][p] is the team playing at home in week w, period p
home = VarArray(size=[n_weeks, n_periods], dom=range(1, n + 1))
# away[w][p] is the team playing away in week w, period p
away = VarArray(size=[n_weeks, n_periods], dom=range(1, n + 1))
# opp[w][i] is the opponent of team i in week w (index 0 is not a team)
opp = VarArray(size=[n_weeks, n + 1], dom=range(0, n + 1))

satisfy(
    # every team plays once a week
    [AllDifferent(home[w] + away[w]) for w in range(n_weeks)],

    # every team plays at most twice in the same period over the tournament
    [Count([home[w][p] for w in range(n_weeks)] + [away[w][p] for w in range(n_weeks)], value=i) <= 2
     for p in range(n_periods) for i in range(1, n + 1)],

    # the opponent table agrees with the matches in each week
    [opp[w][0] == 0 for w in range(n_weeks)],
    [opp[w][home[w][p]] == away[w][p] for w in range(n_weeks) for p in range(n_periods)],
    [opp[w][away[w][p]] == home[w][p] for w in range(n_weeks) for p in range(n_periods)],
    [opp[w][i] != i for w in range(n_weeks) for i in range(1, n + 1)],

    # every team plays every other team: its opponents over the weeks are all different
    [AllDifferent([opp[w][i] for w in range(n_weeks)]) for i in range(1, n + 1)],
)
