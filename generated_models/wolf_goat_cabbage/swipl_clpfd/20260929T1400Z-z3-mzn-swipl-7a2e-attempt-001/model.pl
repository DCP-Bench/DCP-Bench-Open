:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Wolf, goat and cabbage: a farmer ferries a wolf, a goat and a cabbage across
% a river in a boat that carries the farmer and at most one item. The wolf must
% never be left alone with the goat, nor the goat with the cabbage. The answer
% lists, for each stage, which shore (0 = start, 1 = destination) each item and
% the boat are on.
model(Instance, Vars,
      [wolf_pos-Wolf, goat_pos-Goat, cabbage_pos-Cabbage, boat_pos-Boat]) :-
    Stage = Instance.stage,   % number of stages, including the first and the last
    length(Wolf, Stage),
    length(Goat, Stage),
    length(Cabbage, Stage),
    length(Boat, Stage),
    append([Wolf, Goat, Cabbage, Boat], Vars),
    Vars ins 0..1,

    % everything starts on the first shore ...
    Wolf = [0|_], Goat = [0|_], Cabbage = [0|_], Boat = [0|_],
    % ... and ends on the far shore
    last(Wolf, 1), last(Goat, 1), last(Cabbage, 1), last(Boat, 1),

    % the boat crosses the river at every stage
    crosses(Boat),

    % every stage: nobody is left alone with someone who would eat them
    stages(Wolf, Goat, Cabbage, Boat),

    % at most one of the wolf, goat and cabbage changes shore between two stages
    moves(Wolf, Goat, Cabbage).

crosses([_]).
crosses([A, B|Rest]) :-
    A #\= B,
    crosses([B|Rest]).

stages([], [], [], []).
stages([W|Ws], [G|Gs], [C|Cs], [B|Bs]) :-
    % the wolf and the goat are never alone together: if they share a shore the boat is there too
    (G #\= W) #\/ (B #= W),
    % the goat and the cabbage are never alone together
    (G #\= C) #\/ (B #= G),
    stages(Ws, Gs, Cs, Bs).

moves([_], [_], [_]).
moves([W1, W2|Ws], [G1, G2|Gs], [C1, C2|Cs]) :-
    abs(W1 - W2) + abs(G1 - G2) + abs(C1 - C2) #=< 1,
    moves([W2|Ws], [G2|Gs], [C2|Cs]).
