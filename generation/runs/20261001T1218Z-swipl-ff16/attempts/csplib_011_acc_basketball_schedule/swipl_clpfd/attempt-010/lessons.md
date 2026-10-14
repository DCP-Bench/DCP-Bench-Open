# Lessons (swipl_clpfd)

What changed a 180 s timeout into 44 s, over attempts 001 to 010:

1. Model the schedule as 0/1 "who hosts whom" cells (as the picat model does)
   instead of opponent integers with reified conjunctions (attempts 001-002).
2. State implied sums for propagation: per day as many home as away teams,
   every pair meets once over the nine pairs of days, one bye per team.
3. Generate, with findall/3 over plain Prolog arithmetic, the table of all
   per-team place sequences that pass the rules which involve one team only
   (3^9 candidates), and post `tuples_in/2` on each team's places. The rules
   as sums over windows propagate far too weakly for the search to ever finish.
4. Label in an explicit order with `labeling_options([leftmost])`: the
   per-team places first, then pair of days by pair of days (who meets, who is
   at home, who hosts whom). With the default `ff` the 0/1 cells are labelled
   before the 3-valued places, because ff prefers the smaller domain.
5. Slips found on the way: `Bye #= 1 - Home - Away` needs `Bye in 0..1`
   (attempt-004 returned schedules with two games a day).
