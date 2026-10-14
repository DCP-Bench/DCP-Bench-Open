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

    % The pieces are split in two groups. Each group has a signed sum for every
    % way of placing its pieces (-1 left pan, 0 off the scale, 1 right pan).
    % A weight is weighed when a sum of the first group and a sum of the second
    % add up to it.
    HalfSize is N // 2,
    length(First, HalfSize),
    append(First, Second, Weights),
    signed_sums(First, M, FirstSums),
    signed_sums(Second, M, SecondSums),

    % every weight from 1 to m is a sum of the first group plus one of the
    % second. The two parts of each weight (FirstPart, SecondPart) are not
    % searched for: once the pieces are known, their domains hold exactly the
    % possible sums, and FirstPart + SecondPart = Weight is a constraint
    % between two variables that is checked completely. Leaving them out of
    % Vars keeps each set of pieces from being reported once per way of
    % weighing every weight.
    MinusM is -M,
    numlist(1, M, Targets),
    maplist({FirstSums, SecondSums, MinusM, M}/[Target]>>(
                FirstPart in MinusM..M,
                SecondPart in MinusM..M,
                element(_, FirstSums, FirstPart),
                element(_, SecondSums, SecondPart),
                FirstPart + SecondPart #= Target),
            Targets),
    append([Weights, FirstSums, SecondSums], Vars).

% The signed sums of the pieces over every placement of them: 3^(number of pieces).
signed_sums(Pieces, M, Sums) :-
    length(Pieces, Count),
    findall(Placement, placement(Count, Placement), Placements),
    MinusM is -M,
    maplist({Pieces, MinusM, M}/[Placement, Sum]>>(
                Sum in MinusM..M,
                scalar_product(Placement, Pieces, #=, Sum)),
            Placements, Sums).

% A placement of Count pieces: each is -1, 0 or 1.
placement(0, []) :- !.
placement(Count, [Side|Sides]) :-
    Next is Count - 1,
    member(Side, [-1, 0, 1]),
    placement(Next, Sides).

% The pieces are decided in order.
labeling_options([leftmost]).
