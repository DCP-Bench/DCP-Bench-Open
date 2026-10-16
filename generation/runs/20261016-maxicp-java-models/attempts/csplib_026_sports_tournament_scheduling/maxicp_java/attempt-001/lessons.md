# Lessons: csplib_026_sports_tournament_scheduling, maxicp_java, attempt-001

Result: not retained. The evaluator skipped the 8-team example with execution_timeout (180 s, no solution found), so 1 of 2 instances is checked (50%, below the 80% rule). The 6-team instance (json:1) is accepted with 2 solutions in about 2 s.

What the search needed, from the free checks:
- Pair-meeting booleans built from products of slot booleans, with home and away integers as decisions, did not finish the 8-team example in 180 s, even with an opponent allDifferent per team.
- Each team must play once a week, stated per team and week as a sum over that week's slots. Without it a week can repeat a team, and the evaluator rejects that with invalid_solution.
- The implied constraint that each team plays at least once in each period (n-1 games, at most 2 per period) took the 6-team case from timeout to about 2 s.
- Modelling each week as a perfect matching (one meet boolean per unordered pair and week, an exact-one sum per team and week, a clause per ordered pair linking a slot to the matching) is the fastest encoding tried, but the final version still timed out on the 8-team example.
- Flipping the polarity of the decision booleans (branch on assigning first) did not change the 8-team result.

Open question: the description says teams are numbered 1 to n, while its 8-team example table uses 0 to 7. The numbering runs were made on a variant that lacked the once-a-week constraint, so they do not settle which numbering the reference expects.
