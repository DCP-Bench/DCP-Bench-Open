% Archery puzzle: how close can the young archer come to scoring a total of a
% target score, using as many arrows as she pleases, when the targets are
% given as a list of integers? Minimise the deviation from the target score
% and report the number of hits on each target.

:- lib(ic).

model(Instance, Vars, [hits-Hits], min(Dev)) :-
    memberchk(targets-Ts, Instance),
    memberchk(target_score-T, Instance),
    length(Ts, N),
    length(Hits, N),

    % number of hits on each target: a bound derived here, not in the statement.
    % In an optimal solution no target has more than target_score div score + 1
    % hits, since removing one arrow from a total above the target score moves
    % the total closer to the target score.
    ( foreach(Ti, Ts), foreach(H, Hits), foreach(Term, Terms), param(T) do
        Ub is T // Ti + 1,
        H :: 0..Ub,
        Term #= H * Ti
    ),

    % the total score is the hits on each target times its ring score, summed;
    % the deviation is the distance of that total from the target score.
    Total #= sum(Terms),
    Dev #= abs(Total - T),

    Vars = Hits.
