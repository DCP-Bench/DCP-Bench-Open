:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Map colouring: adjacent countries differ in colour, and the highest colour
% number used is as small as possible.
model(Instance, Colors, [colors-Colors], min(Used)) :-
    Graph = Instance.graph,
    % The instance carries only the edge list, so the country count is the
    % largest 1-based country id appearing in it.
    append(Graph, Endpoints),
    max_list(Endpoints, NumNodes),
    length(Colors, NumNodes),
    % Colours run 1..num_nodes, as in the reference.
    Colors ins 1..NumNodes,
    maplist({Colors}/[Edge]>>different_colour(Colors, Edge), Graph),
    max_member_constraint(Colors, Used).

different_colour(Colors, [I, J]) :-
    nth1(I, Colors, Here),
    nth1(J, Colors, There),
    Here #\= There.

% The number of colours used is the largest colour number on the map.
max_member_constraint([C|Cs], Max) :-
    foldl([X, Acc0, Acc]>>(Acc #= max(Acc0, X)), Cs, C, Max).
