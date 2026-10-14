:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(pairs)).
:- use_module(library(yall)).

% Cabling: place n devices in the slots of a rack cabinet, one device per slot,
% so that the total length of the cables joining them is as short as possible.
% A cable between two devices is as long as the number of slots between them,
% and a connection may need several cables.
model(Instance, Vars, [final_sum-FinalSum], min(FinalSum)) :-
    N = Instance.n,
    Devices = Instance.devices,         % device names, in the order devices are numbered
    Cables = Instance.cable_struct,     % [DeviceA, DeviceB, NumberOfCables]

    % X[d] = slot (numbered from 0) of device d in the rack
    Top is N - 1,
    length(X, N),
    X ins 0..Top,

    % each device has its own slot
    all_distinct(X),

    % T[i] = length of connection i: the slot distance of its two devices times
    % its number of cables; the reference bounds it by 1..n*n
    MaxLength is N * N,
    maplist(connection_length(Devices, X, MaxLength), Cables, Lengths),

    % the total cable length, which is minimised; it is bounded by n*n times the
    % number of cables in all, as in the reference
    maplist(cable_count, Cables, Counts),
    sum_list(Counts, TotalCables),
    MaxTotal is N * N * TotalCables,
    FinalSum in 0..MaxTotal,
    sum(Lengths, #=, FinalSum),

    % Devices with many cables are placed first (their position decides most of
    % the cost). Mirroring the rack gives another arrangement of the same cost,
    % so the first of them is kept in the lower half of the rack.
    numlist(0, Top, Numbers),
    maplist(device_weight(Devices, Cables), Devices, Weights),
    pairs_keys_values(Keyed0, Weights, Numbers),
    maplist([W-D, NW-D]>>(NW is -W), Keyed0, Keyed),
    keysort(Keyed, Sorted),
    pairs_values(Sorted, Order),
    maplist({X}/[D, Slot]>>nth0(D, X, Slot), Order, OrderedX),
    OrderedX = [First|_],
    2 * First #=< Top,
    append(OrderedX, [FinalSum|Lengths], Vars).

% Length of the connection between two named devices carrying Count cables.
connection_length(Devices, X, MaxLength, [NameA, NameB, Count], Length) :-
    nth0(A, Devices, NameA),
    nth0(B, Devices, NameB),
    nth0(A, X, SlotA),
    nth0(B, X, SlotB),
    Length in 1..MaxLength,
    Length #= abs(SlotA - SlotB) * Count.

cable_count([_, _, Count], Count).

% Total number of cables at a device.
device_weight(_, Cables, Name, Weight) :-
    foldl({Name}/[[A, B, Count], W0, W]>>(
              (   ( A == Name ; B == Name ) -> W is W0 + Count ; W = W0 )),
          Cables, 0, Weight).

labeling_options([leftmost]).
