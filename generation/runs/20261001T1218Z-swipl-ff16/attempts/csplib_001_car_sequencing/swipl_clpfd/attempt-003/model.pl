:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(pairs)).
:- use_module(library(yall)).

% Car sequencing: order the cars on an assembly line so that every option
% station copes. Option o may be needed by at most at_most[o] cars in any
% window of per_slots[o] consecutive cars, and each car type is built exactly
% as often as it is demanded.
model(Instance, Vars, [sequence-Sequence]) :-
    AtMost = Instance.at_most,       % cars needing option o allowed per window
    PerSlots = Instance.per_slots,   % window length of option o
    Demand = Instance.demand,        % number of cars wanted of each type
    Requires = Instance.requires,    % Requires[t][o] = 1 if type t needs option o

    % one car per slot of the line: the number of cars is the total demand
    sum_list(Demand, NCars),
    length(Demand, NTypes),
    Top is NTypes - 1,
    numlist(0, Top, Types),

    % The search tries car types in the order of Order, which is the types sorted
    % by how heavily the options they need are used (most used first), as in the
    % usual car sequencing heuristic. Without this order the search does not
    % finish on the 200-car instances. Ranks[s] is the position in Order of the
    % type of the car in slot s, and Sequence[s] is that type itself.
    transpose(Requires, RequiresByOption),
    maplist(option_total(Demand), RequiresByOption, Totals),
    maplist(type_key(Requires, Totals, PerSlots, AtMost, NCars), Types, Keyed),
    keysort(Keyed, Sorted),
    pairs_values(Sorted, Order),
    length(Ranks, NCars),
    Ranks ins 0..Top,
    length(Sequence, NCars),
    maplist(type_of_rank(Order), Ranks, Sequence),

    % the number of cars of each type in the sequence equals its demand
    maplist(pick(Demand), Order, RankedDemand),
    pairs_keys_values(Counts, Types, RankedDemand),
    global_cardinality(Ranks, Counts),

    % Setups[o][s] = 1 when the car in slot s needs option o
    maplist(pick(Requires), Order, RankedRequires),
    transpose(RankedRequires, RankedByOption),
    maplist(setup_of_option(Ranks), RankedByOption, Setups),

    % no station is overloaded: in every window of per_slots[o] consecutive
    % slots at most at_most[o] cars need option o
    maplist(windows_ok, Setups, PerSlots, AtMost),

    % implied: the cars needing option o are spread evenly enough along the line
    maplist(implied_counts(NCars), Setups, PerSlots, AtMost, Totals),

    % only the ranks are chosen; the setups and the sequence follow from them
    Vars = Ranks.

% Item at position Index (from 0) of List.
pick(List, Index, Item) :- nth0(Index, List, Item).

% Cars in all that need an option, given which types need it.
option_total(Demand, RequiresOfOption, Total) :-
    foldl([D, R, S0, S]>>(S is S0 + D * R), Demand, RequiresOfOption, 0, Total).

% Sort key of a type: minus the sum, over the options it needs, of how heavily
% the option is used (cars needing it, over what its windows allow, scaled by 1000).
type_key(Requires, Totals, PerSlots, AtMost, NCars, Type, Key-Type) :-
    nth0(Type, Requires, Row),
    foldl({NCars}/[R, Total, Q, P, S0, S]>>(
              Use is Total * Q * 1000 // (NCars * max(P, 1)),
              S is S0 + R * Use),
          Row, Totals, PerSlots, AtMost, 0, Score),
    Key is -Score.

% The type at a rank. element/3 counts from 1, ranks from 0.
type_of_rank(Order, Rank, Type) :-
    Index #= Rank + 1,
    element(Index, Order, Type).

% Setup[s] = 1 when the car of rank Rank[s] needs the option.
setup_of_option(Ranks, RequiresOfOption, Setup) :-
    maplist(needs_option(RequiresOfOption), Ranks, Setup).

needs_option(RequiresOfOption, Rank, Needs) :-
    Index #= Rank + 1,
    element(Index, RequiresOfOption, Needs).

% Every window of Width consecutive entries of Setup holds at most Limit ones.
% A line shorter than the window has no window and nothing to check.
windows_ok(Setup, Width, Limit) :-
    length(Setup, Length),
    (   Length < Width
    ->  true
    ;   length(Window, Width),
        append(Window, _, Setup),
        sum(Window, #=<, Limit),
        Setup = [_|Rest],
        windows_ok(Rest, Width, Limit)
    ).

% Running count of cars needing the option, with the range each count can take.
% The first i slots hold at most max_prefix(i) such cars (Limit per full window
% plus what a partial window can add), and the remaining slots hold at most
% max_prefix(Length - i) of the Total, so at least Total - max_prefix(Length - i)
% are among the first i. These bounds follow from the window rule; they only
% help the search.
implied_counts(Length, Setup, Width, Limit, Total) :-
    (   Length < Width
    ->  true
    ;   numlist(1, Length, Sizes),
        maplist(count_range(Length, Width, Limit, Total), Sizes, Counts),
        foldl([S, C, C0, C]>>(C #= C0 + S), Setup, Counts, 0, Total)
    ).

count_range(Length, Width, Limit, Total, Size, Count) :-
    Rest is Length - Size,
    Hi is min(Total, Limit * (Size // Width) + min(Limit, Size mod Width)),
    Lo is max(0, Total - (Limit * (Rest // Width) + min(Limit, Rest mod Width))),
    Count in Lo..Hi.

% Smallest domain first: the slot with the fewest types still possible is
% filled next, trying the most heavily used types first.
labeling_options([ff]).
