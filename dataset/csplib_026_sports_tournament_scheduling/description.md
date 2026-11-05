The problem is to schedule a tournament of \( n \) teams over \( n-1 \) weeks, with each week divided into \( n/2 \)
periods, and each period divided into two slots. The first team in each slot plays at home, whilst the second plays
the first team away. A tournament must satisfy the following three constraints: every team plays once a week; every
team plays at most twice in the same period over the tournament; every team plays every other team.

An example schedule for 8 teams is:

| Week 1  | Week 2  | Week 3  | Week 4  | Week 5  | Week 6  | Week 7  |
|---------|---------|---------|---------|---------|---------|---------|
| 0 v 1   | 0 v 2   | 4 v 7   | 3 v 6   | 3 v 7   | 1 v 5   | 2 v 4   |
| 2 v 3   | 1 v 7   | 0 v 3   | 5 v 7   | 1 v 4   | 0 v 6   | 5 v 6   |
| 4 v 5   | 3 v 5   | 1 v 6   | 0 v 4   | 2 v 6   | 2 v 7   | 0 v 7   |
| 6 v 7   | 4 v 6   | 2 v 5   | 1 v 2   | 0 v 5   | 3 v 4   | 1 v 3   |

Print the home and away schedules (home, away) as lists of lists, where, e.g. home[w][p] is the team playing
home in week w and period p. The teams are numbered from 1 to n.
