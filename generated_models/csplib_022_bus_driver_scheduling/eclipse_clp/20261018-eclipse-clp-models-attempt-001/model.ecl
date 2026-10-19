% csplib_022_bus_driver_scheduling: bus driver scheduling.
% Select a subset of shifts so that every piece of work is covered by
% exactly one selected shift, minimising the number of selected shifts.
% x[j] = 1 means shift j is selected.

:- lib(ic).

% Each piece of work is covered by exactly one selected shift.
model(Instance, X, [x-X], min(sum(X))) :-
    memberchk(num_shifts-NS, Instance),
    memberchk(num_work-NW, Instance),
    memberchk(shifts-Shifts, Instance),
    length(X, NS),
    X :: 0..1,
    cover_all(0, NW, Shifts, X).

cover_all(W, NW, _, _) :-
    W >= NW, !.
cover_all(W, NW, Shifts, X) :-
    covering_vars(W, Shifts, X, Cov),
    sum(Cov) #= 1,
    W1 is W + 1,
    cover_all(W1, NW, Shifts, X).

% The variables of the shifts that contain work W.
covering_vars(_, [], [], []).
covering_vars(W, [S|Ss], [V|Vs], Out) :-
    (   memberchk(W, S)
    ->  Out = [V|Out1]
    ;   Out = Out1
    ),
    covering_vars(W, Ss, Vs, Out1).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
