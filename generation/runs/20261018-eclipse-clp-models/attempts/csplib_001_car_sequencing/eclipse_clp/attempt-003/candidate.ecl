% CSPLib 001 car sequencing: produce cars of different types on an assembly
% line so that each option station is never over capacity.
% Output: sequence, the car type (0-based) at each position of the line.
%
% Encoding: Rank[s] in 1..T is a rank of the car type at position s. The types
% are ordered in Prolog by how heavily they load the option stations (a search
% order computed from the instance data). Seq[s] is the type at that rank, via
% element/3. Per option, Setup[s] tells whether position s needs the option,
% and prefix counts Count[k] bound the cars with the option among the first k
% positions. A window of per_slots consecutive positions holds at most at_most
% cars with the option.

:- lib(ic).
:- lib(ic_global).
:- lib(ic_global_gac).
:- lib(listut).
:- import alldifferent/1 from ic_global.

% Vars (the rank of each position) is what the driver labels; Seq follows from it.
model(Instance, Rank, [sequence-Seq]) :-
    memberchk(demand-Demand, Instance),
    memberchk(at_most-AtMost, Instance),
    memberchk(per_slots-PerSlots, Instance),
    memberchk(requires-Requires, Instance),
    length(Demand, T),
    length(AtMost, NO),
    ( foreach(D, Demand), fromto(0, A0, A1, L) do A1 is A0 + D ),
    L1 is L + 1,

    % the total demand of each option, and the order of the types by station load
    option_totals(0, NO, Demand, Requires, Totals),
    order_types(T, NO, Requires, Totals, PerSlots, AtMost, Order),

    % the rank of each position, the number of positions per rank, and the type
    length(Rank, L),
    Rank :: 1..T,
    rank_demand(Order, Demand, DemandByRank),
    ( foreach(Dr, DemandByRank), fromto(1, R0, R1, _), foreach(gcc(Dr, Dr, R0), Specs) do
        R1 is R0 + 1
    ),
    gcc(Specs, Rank),
    length(Seq, L),
    ( foreach(R, Rank), foreach(S, Seq), param(Order, T) do
        S :: 0..T-1,
        element(R, Order, S)
    ),

    % cars requiring option o must not be bunched together: a station
    % handles at most at_most[o] cars among any per_slots[o] consecutive cars
    ( for(O, 0, NO-1),
      param(Requires, AtMost, PerSlots, Totals, Order, Rank, L, L1) do
        nth0(O, AtMost, M),
        nth0(O, PerSlots, Q),
        nth0(O, Totals, Tot),
        option_column(Order, Requires, O, Col),
        length(Setup, L),
        Setup :: 0..1,
        ( foreach(R, Rank), foreach(Sv, Setup), param(Col) do
            element(R, Col, Sv)
        ),
        length(Counts, L1),
        Counts :: 0..Tot,
        prefix_counts(Counts, Setup, 0),
        nth0(0, Counts, C0), C0 #= 0,
        nth0(L, Counts, CL), CL #= Tot,
        ( for(K, 0, L), param(Counts, Q, M, Tot, L) do
            count_bounds(K, Q, M, L, Tot, Lo, Hi),
            nth0(K, Counts, Ck),
            Ck #>= Lo,
            Ck #=< Hi
        ),
        ( for(P, 0, L-Q), param(Counts, Q, M) do
            Pq is P + Q,
            nth0(P, Counts, Cp),
            nth0(Pq, Counts, Cpq),
            Cpq - Cp #=< M
        )
    ).

% Counts[k+1] = Counts[k] + Setup[k] for k = I .. L-1
prefix_counts(Counts, Setup, I) :-
    ( nth0(I, Setup, Sk) ->
        I1 is I + 1,
        nth0(I, Counts, Ck),
        nth0(I1, Counts, Ck1),
        Ck1 #= Ck + Sk,
        prefix_counts(Counts, Setup, I1)
    ;
        true
    ).

% the total demand of option O over all types (Demand weighted by Requires)
option_totals(NO, NO, _, _, []) :- !.
option_totals(O, NO, Demand, Requires, [Tot|Rest]) :-
    option_total(Demand, Requires, O, 0, Tot),
    O1 is O + 1,
    option_totals(O1, NO, Demand, Requires, Rest).

option_total([], [], _, Acc, Acc).
option_total([D|Ds], [Row|Rows], O, Acc, Tot) :-
    nth0(O, Row, V),
    Acc1 is Acc + D * V,
    option_total(Ds, Rows, O, Acc1, Tot).

% the 0/1 need of option O for the car types in rank order
option_column(Order, Requires, O, Col) :-
    ( foreach(Ty, Order), foreach(C, Col), param(Requires, O) do
        nth0(Ty, Requires, Row),
        nth0(O, Row, C)
    ).

% the number of cars of each type, in rank order
rank_demand(Order, Demand, DemandByRank) :-
    ( foreach(Ty, Order), foreach(Dr, DemandByRank), param(Demand) do
        nth0(Ty, Demand, Dr)
    ).

% the bounds on the number of cars with an option among the first K positions
count_bounds(K, Q, M, L, Tot, Lo, Hi) :-
    cap(K, Q, M, CapK),
    R is L - K,
    cap(R, Q, M, CapR),
    Lo is max(0, Tot - CapR),
    Hi is min(Tot, CapK).

% the most cars with an option that fit in K consecutive positions
cap(K, Q, M, Cap) :-
    Cap is (K // Q) * M + min(M, K mod Q).

% the types in order of decreasing station load (the search order)
order_types(T, NO, Requires, Totals, PerSlots, AtMost, Order) :-
    type_keys(0, T, NO, Requires, Totals, PerSlots, AtMost, Keys),
    keysort(Keys, Sorted),
    ( foreach(_-Ty, Sorted), foreach(Ty, Order) do true ).

% Keys: negated station load of each type, paired with the type
type_keys(T, T, _, _, _, _, _, []) :- !.
type_keys(Ty, T, NO, Requires, Totals, PerSlots, AtMost, [Key-Ty|Rest]) :-
    nth0(Ty, Requires, Row),
    option_load(0, NO, Row, Totals, PerSlots, AtMost, 0.0, S),
    Key is -S,
    Ty1 is Ty + 1,
    type_keys(Ty1, T, NO, Requires, Totals, PerSlots, AtMost, Rest).

option_load(NO, NO, _, _, _, _, S, S) :- !.
option_load(O, NO, Row, Totals, PerSlots, AtMost, S0, S) :-
    nth0(O, Row, R),
    nth0(O, Totals, Tot),
    nth0(O, PerSlots, P),
    nth0(O, AtMost, M),
    S1 is S0 + R * Tot * P / (M * 1.0),
    O1 is O + 1,
    option_load(O1, NO, Row, Totals, PerSlots, AtMost, S1, S).

search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_min, complete, []).
