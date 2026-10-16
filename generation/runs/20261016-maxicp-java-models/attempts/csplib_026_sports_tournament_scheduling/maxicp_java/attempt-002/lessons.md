# Lessons: csplib_026_sports_tournament_scheduling, maxicp_java, attempt-002

Result: not retained. The evaluator accepted json:1 (6 teams, 2 solutions, 1 s). The example (8 teams) hit execution_timeout at 180 s with no solution, so 1 of 2 instances is checked (50%, below the 80% rule). This is a performance limit.

The attempt-002 model is a one-hot encoding: booleans hm[w][p][t] (team t at home in period p of week w) and aw[w][p][t], exactly one per slot and per team-week, at most two and at least one per team-period, and a meet boolean per pair, period and week that forces exactly one meeting per pair.

Free checks on the 8-team example (60 to 180 s each, none found a solution in time unless noted):

- Integer home/away decisions with element-based opponent matrix and allDifferent per team over weeks (the attempt-002 first draft, then the one-hot model's predecessor): timeout.
- Adding pair-meeting redundancy built from isOr(isEq(...)) booleans: timeout.
- One-hot booleans (above): timeout; 6-team instance solved in 1 s.
- Same model without the period constraints: two solutions in 0.9 s, but both rejected with invalid_solution ("Declared outputs cannot extend to a reference solution"). The period constraint is the hard part.
- Same model without the at-least-once constraint: timeout.
- Registration order period-major instead of week-major: timeout.
- Flipped polarity of the boolean decisions (not(m.boolVar())): timeout.
- Slot-permutation model (allDifferent over pair slots, element views for week and period): timeout, and without the period constraints also no solution in 60 s, so element views with allDifferent propagate too weakly here.

Reading of the evidence: plain DFS with no learning does not reach a period-feasible tournament for 8 teams in 180 s under any of these encodings. Symmetry breaking would likely help, but the contract forbids symmetry breaking the description does not ask for, so it was not tried.

Open question (carried from attempt-001): the description says teams are numbered 1 to n, while the example table uses 0 to 7. This model uses 1 to n, as the description states. The 8-team example is where the numbering would show up, and it was never reached.

Suggested next steps for a later attempt, if the team wants one: a model that adds redundant period-usage reasoning per team (exactly one period with count one), or a larger time budget for this pair. Neither was tried here.
