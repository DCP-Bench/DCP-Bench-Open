% Wolf, goat and cabbage river crossing.
% A farmer with a wolf, a goat and a cabbage must cross a river by boat. The boat can
% carry only the farmer and a single item. If left unattended together, the wolf would
% eat the goat, or the goat would eat the cabbage. How can they cross the river without
% anything being eaten?
% Each stage gives the shore of the wolf, goat, cabbage and boat: 0 is the starting
% shore, 1 the destination shore.
:- lib(ic).
:- lib(listut).

model(Instance, Vars, Outputs) :-
    memberchk(stage-N, Instance),
    length(Bs, N), length(Ws, N), length(Gs, N), length(Cs, N),
    flatten([Bs, Ws, Gs, Cs], Vars),
    Vars :: 0..1,

    % The stages start with everything on the starting shore and end with
    % everything on the destination shore.
    nth1(1, Bs, 0), nth1(1, Ws, 0), nth1(1, Gs, 0), nth1(1, Cs, 0),
    nth1(N, Bs, 1), nth1(N, Ws, 1), nth1(N, Gs, 1), nth1(N, Cs, 1),

    % The wolf would eat the goat, or the goat would eat the cabbage, if left
    % unattended together: at every stage, the farmer must be with the goat when
    % the wolf and goat share a shore, and with the cabbage when the goat and
    % cabbage share a shore.
    ( foreach(B, Bs), foreach(W, Ws), foreach(G, Gs), foreach(C, Cs) do
        (W #\= G) or (B #= G),
        (G #\= C) or (B #= C)
    ),

    % The boat can carry only the farmer and a single item. Every stage the boat
    % crosses, and the farmer takes at most one item: an item that moves was on
    % the farmer's shore, and at most one of wolf, goat and cabbage moves.
    transitions(Bs, Ws, Gs, Cs),

    Outputs = ['wolf_pos'-Ws, 'goat_pos'-Gs, 'cabbage_pos'-Cs, 'boat_pos'-Bs].

transitions([B1, B2 | Bs], [W1, W2 | Ws], [G1, G2 | Gs], [C1, C2 | Cs]) :-
    B1 #\= B2,
    (W1 #= W2) or (W1 #= B1),
    (G1 #= G2) or (G1 #= B1),
    (C1 #= C2) or (C1 #= B1),
    (W1 #= W2) or (G1 #= G2),
    (W1 #= W2) or (C1 #= C2),
    (G1 #= G2) or (C1 #= C2),
    transitions([B2 | Bs], [W2 | Ws], [G2 | Gs], [C2 | Cs]).
transitions([_], [_], [_], [_]).
