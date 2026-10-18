% Archery puzzle: a young archer shoots as many arrows as she likes. Each target
% i scores targets[i] per hit. hits[i] is the number of arrows on target i.
% How close can the archer come to a total of target_score? Minimise the
% deviation |total - target_score|, and report the hits.

:- lib(ic).

model(Instance, Vars, [hits-Hits], min(Dev)) :-
    memberchk(targets-Ts, Instance),
    memberchk(target_score-T, Instance),
    length(Ts, N),
    length(Hits, N),

    % Each hit count is bounded by the target score: one more arrow than
    % T div score on a ring is never needed to get closest to the target.
    ( foreach(Ti, Ts), foreach(H, Hits), foreach(Term, Terms), param(T) do
        Ub is T // Ti + 1,
        H :: 0..Ub,
        Term #= H * Ti
    ),

    % The total score of all arrows, and the deviation from the target score.
    % The total is the sum of hits times ring scores.
    Total #= sum(Terms),
    Dev #= abs(Total - T),

    Vars = Hits.
