% Choose 3 of 5 people for a team at the lowest total cost, then list every team
% that reaches that cost.
% Shows: minimise with labeling([min(Expr)]), all optimal solutions by fixing the
% optimum (Cost #= Opt) and enumerating, and a 0/1 selection with sum/3.
:- use_module(library(clpfd)).
:- initialization(main, main).

costs([3, 1, 4, 1, 3]).

% Pick[i] is 1 when person i is in the team.
team(Pick, Cost) :-
    costs(Costs),
    length(Costs, N),
    length(Pick, N),
    Pick ins 0..1,
    sum(Pick, #=, 3),
    scalar_product(Costs, Pick, #=, Cost).

main :-
    team(Pick, Cost),
    once(labeling([min(Cost)], Pick)),
    Optimum is Cost,
    format("Optimal cost: ~w~n", [Optimum]),
    findall(Team, (team(Team, TeamCost), TeamCost #= Optimum, label(Team)), Best),
    length(Best, Count),
    format("Optimal teams: ~w~n", [Count]),
    forall(member(Team, Best), (format("  ~w~n", [Team]))).
