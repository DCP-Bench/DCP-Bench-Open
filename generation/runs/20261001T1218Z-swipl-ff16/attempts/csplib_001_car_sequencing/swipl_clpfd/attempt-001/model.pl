:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
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
    length(Sequence, NCars),
    Sequence ins 0..Top,

    % the number of cars of each type in the sequence equals its demand
    numlist(0, Top, Types),
    pairs_keys_values(Counts, Types, Demand),
    global_cardinality(Sequence, Counts),

    % Setups[o][s] = 1 when the car in slot s needs option o. Types are numbered
    % from 0 and element/3 counts from 1, hence the shifted index.
    transpose(Requires, RequiresByOption),
    maplist({Sequence}/[RequiresOfOption, SetupOfOption]>>
                maplist({RequiresOfOption}/[Type, Needs]>>(
                            Index #= Type + 1,
                            element(Index, RequiresOfOption, Needs)),
                        Sequence, SetupOfOption),
            RequiresByOption, Setups),

    % no station is overloaded: in every window of per_slots[o] consecutive
    % slots at most at_most[o] cars need option o
    maplist(windows_ok, Setups, PerSlots, AtMost),
    append([Sequence|Setups], Vars).

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
