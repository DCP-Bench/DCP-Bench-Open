% CSPLib 001 car sequencing: produce cars of different types on an assembly
% line so that each option station is never over capacity.
% Output: sequence, the car type (0-based) at each position of the line.

:- lib(ic).
:- lib(ic_global).
:- lib(listut).
:- import alldifferent/1 from ic_global.

model(Instance, Seq, [sequence-Seq]) :-
    memberchk(demand-Demand, Instance),
    memberchk(at_most-AtMost, Instance),
    memberchk(per_slots-PerSlots, Instance),
    memberchk(requires-Requires, Instance),
    length(Demand, T),
    length(AtMost, NO),
    % the line holds every car that is demanded
    ( foreach(D, Demand), fromto(0, A0, A1, L) do A1 is A0 + D ),
    length(Seq, L),
    Seq :: 0..T-1,

    % the number of cars of each type is its demand
    % (type t is demand[t] cars in the sequence)
    ( for(Type, 0, T-1), param(Seq, Demand) do
        nth0(Type, Demand, Dt),
        occurrences(Type, Seq, Dt)
    ),

    % a station never handles more than at_most[o] cars among any per_slots[o]
    % consecutive cars; cars requiring option o must not be bunched together
    ( for(O, 0, NO-1), param(Requires, AtMost, PerSlots, Seq, L) do
        nth0(O, AtMost, M),
        nth0(O, PerSlots, K),
        ( foreach(Row, Requires), foreach(V, Col), param(O) do
            nth0(O, Row, V)
        ),
        ( foreach(S, Seq), foreach(B, Bs), param(Col) do
            I #= S + 1,
            element(I, Col, B)
        ),
        ( for(P, 0, L-K), param(Bs, K, M) do
            post_window(Bs, P, K, M)
        )
    ).

% the sum of the K consecutive entries of Bs starting at position P (0-based)
% is at most M
post_window(Bs, P, K, M) :-
    length(Pre, P),
    append(Pre, Rest, Bs),
    length(Ws, K),
    append(Ws, _, Rest),
    sum(Ws) #=< M.

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
