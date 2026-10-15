There are 13 people. 4 of them are male. -> 13 Bool positions x_i (1 = female), sum(x) == 9 (or 4 males: sum(~x_i) == 4).
They randomly enter a room one at a time. -> one Bool per entry position, sequence is the vector of positions.
the ratio of females to males in the room at any one time is no greater than 7/3 -> for every prefix of length k: 3*f <= 7*m with f = females in prefix, m = k - f, i.e. 10*sum(x[:k]) <= 7*k (linear PB per prefix; forces the first entrant to be male).
Find a way ... -> satisfaction, no objective.
Output sequence -> [13]bool, one Bool per position (1 = female).
