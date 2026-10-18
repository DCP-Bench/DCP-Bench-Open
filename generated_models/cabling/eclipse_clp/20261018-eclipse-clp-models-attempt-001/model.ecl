% Cabling: place the devices of a rack cabinet, one 1U device per position,
% so that the sum of all cable lengths is as short as possible.
% Each cable runs between two devices; its length is the distance between their
% positions. Some devices are connected by several cables, so each cable counts.

:- lib(ic).
:- lib(listut).

model(Instance, Pos, [final_sum-Total], min(Total)) :-
    memberchk(n-N, Instance),
    memberchk(devices-Devs, Instance),
    memberchk(cable_struct-Cables, Instance),

    % The devices are placed in positions 1..n, each position used once.
    length(Pos, N),
    Pos :: 1..N,
    alldifferent(Pos),

    % The sum of all cable lengths: each cable of length |pos(a) - pos(b)|,
    % counted once for each cable between the two devices.
    cable_terms(Cables, Devs, Pos, Terms),
    Total #= sum(Terms).

% One term per cable row [DeviceA, DeviceB, Count]: Count * distance.
cable_terms([], _, _, []).
cable_terms([[A, B, C] | Rest], Devs, Pos, [C * abs(PA - PB) | Terms]) :-
    once(nth1(IA, Devs, A)),
    once(nth1(IB, Devs, B)),
    nth1(IA, Pos, PA),
    nth1(IB, Pos, PB),
    cable_terms(Rest, Devs, Pos, Terms).
