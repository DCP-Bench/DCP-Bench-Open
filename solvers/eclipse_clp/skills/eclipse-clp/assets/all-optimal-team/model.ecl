% Pick 3 of 5 people for the cheapest team, then list every team with that cost.
% bb_options{solutions:all} makes bb_min/3 backtrack through all optimal solutions.
:- lib(ic).
:- lib(branch_and_bound).

costs([3, 1, 4, 1, 3]).

team(Pick, Cost) :-
    costs(Cs),
    length(Cs, N),
    length(Pick, N),
    Pick :: 0..1,
    sum(Pick) #= 3,
    ( foreach(C, Cs), foreach(P, Pick), foreach(T, Ts) do T = C*P ),
    Cost #= sum(Ts).

main :-
    % all optimal solutions in one call
    findall(Pick-Cost,
            ( team(Pick, Cost),
              bb_min(labeling(Pick), Cost,
                     bb_options{solutions:all, report_success:true/0, report_failure:true/0}) ),
            Best),
    length(Best, Count),
    printf("%d optimal teams%n", [Count]),
    ( foreach(P-C, Best) do printf("cost %d: %w%n", [C, P]) ),
    % the same result in two steps: optimum first, then enumerate under that bound
    team(P0, C0),
    bb_min(labeling(P0), C0, bb_options{report_success:true/0, report_failure:true/0}),
    Opt = C0,
    findall(P, ( team(P, C), C #= Opt, labeling(P) ), Again),
    length(Again, Count2),
    printf("two-step check: %d teams at cost %d%n", [Count2, Opt]).
