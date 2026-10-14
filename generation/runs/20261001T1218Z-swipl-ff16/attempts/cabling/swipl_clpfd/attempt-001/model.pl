:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
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
    append([X, Lengths, [FinalSum]], Vars).

% Length of the connection between two named devices carrying Count cables.
connection_length(Devices, X, MaxLength, [NameA, NameB, Count], Length) :-
    nth0(A, Devices, NameA),
    nth0(B, Devices, NameB),
    nth0(A, X, SlotA),
    nth0(B, X, SlotB),
    Length in 1..MaxLength,
    Length #= abs(SlotA - SlotB) * Count.

cable_count([_, _, Count], Count).
