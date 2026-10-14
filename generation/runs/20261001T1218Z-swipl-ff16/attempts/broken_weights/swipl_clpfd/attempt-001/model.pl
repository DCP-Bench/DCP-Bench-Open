:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Broken weights: a weight of m pounds broke into n pieces of whole-pound weight.
% On a balance scale the pieces must be able to weigh every whole weight from 1
% to m, each piece on the left pan, on the right pan, or not used.
model(Instance, Vars, [weights-Weights]) :-
    M = Instance.m,    % total weight of the unbroken weight
    N = Instance.n,    % number of pieces

    % Weights[j] = weight of piece j
    length(Weights, N),
    Weights ins 1..M,

    % the pieces add up to the total weight
    sum(Weights, #=, M),

    % Placement[i][j] says where piece j goes to weigh i + 1 pounds: -1 left
    % pan, 1 right pan, 0 left off the scale
    numlist(1, M, Targets),
    maplist({N}/[_, Row]>>(length(Row, N), Row ins -1..1), Targets, Placement),

    % every weight from 1 to m is the signed sum of the pieces on the scale
    maplist({Weights}/[Target, Row]>>scalar_product(Weights, Row, #=, Target),
            Targets, Placement),

    % labelling the pieces first (listed first in Vars), the placements follow
    append(Placement, PlacementVars),
    append(Weights, PlacementVars, Vars).

% The pieces are the real decisions and have the large domains; the placements
% are searched afterwards in order.
labeling_options([leftmost]).
