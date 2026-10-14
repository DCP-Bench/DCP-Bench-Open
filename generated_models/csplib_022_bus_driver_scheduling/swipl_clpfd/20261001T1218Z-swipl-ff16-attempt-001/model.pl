:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Bus driver scheduling: pick a set of shifts, each covering some pieces of
% work, so that every piece of work is covered by exactly one chosen shift and
% as few shifts as possible are used.
model(Instance, Vars, [x-X], min(NumChosen)) :-
    NumWork = Instance.num_work,       % pieces of work, numbered from 0
    Shifts = Instance.shifts,          % Shifts[i] = the pieces of work shift i covers

    % X[i] is 1 when shift i is chosen
    length(Shifts, NumShifts),
    length(X, NumShifts),
    X ins 0..1,

    % every piece of work is covered by exactly one chosen shift
    Last is NumWork - 1,
    numlist(0, Last, Work),
    maplist(covered_once(Shifts, X), Work),

    % the number of chosen shifts, which is minimised (every shift costs the same)
    sum(X, #=, NumChosen),
    Vars = X.

% Exactly one of the chosen shifts contains piece of work Task.
covered_once(Shifts, X, Task) :-
    findall(I, (nth0(I, Shifts, Shift), memberchk(Task, Shift)), Covering),
    maplist({X}/[I, Var]>>nth0(I, X, Var), Covering, CoveringVars),
    sum(CoveringVars, #=, 1).
