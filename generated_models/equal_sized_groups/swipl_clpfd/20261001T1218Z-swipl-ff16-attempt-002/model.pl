:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Equal sized groups: cut a sorted list of N elements into K consecutive
% groups by choosing K-1 break points, so that equal elements stay in the same
% group and the group sizes are as close as possible to round(N/K). The error is
% the sum of the differences between each group size and that ideal size.
model(Instance, Vars, [x-Breaks], min(Error)) :-
    A = Instance.a,    % the sorted elements
    K = Instance.k,    % number of groups

    length(A, N),
    % ideal group size round(N/K); the reference rounds with Python's round,
    % which sends an exact half to the even neighbour
    Quotient is N // K,
    Remainder is N mod K,
    (   2 * Remainder < K
    ->  GroupSize = Quotient
    ;   2 * Remainder > K
    ->  GroupSize is Quotient + 1
    ;   Quotient mod 2 =:= 0
    ->  GroupSize = Quotient
    ;   GroupSize is Quotient + 1
    ),

    % Sizes[g] = number of elements of group g; Breaks[g] = number of elements
    % before the break that ends group g (break points are 1-based indexes)
    NumBreaks is K - 1,
    length(Sizes, K),
    Sizes ins 1..N,
    length(Breaks, NumBreaks),
    Breaks ins 1..N,

    % the first group ends at the first break, each middle group is the gap
    % between two breaks, and the last group is what remains after the last break
    Sizes = [First|Rest],
    Breaks = [FirstBreak|_],
    First #= FirstBreak,
    sizes_between_breaks(Breaks, Rest, N),

    % elements with the same value stay together: no break may fall between two
    % equal neighbours, so a break after the first j elements is forbidden
    % when element j equals element j + 1
    equal_neighbours(A, 1, NoBreakAt),
    maplist({NoBreakAt}/[Break]>>maplist({Break}/[J]>>(Break #\= J), NoBreakAt), Breaks),

    % error: how far the group sizes are from the ideal size in total
    MaxError = N,
    Error in 0..MaxError,
    maplist({GroupSize}/[Size, Deviation]>>(Deviation #= abs(Size - GroupSize)), Sizes, Deviations),
    sum(Deviations, #=, Error),
    % Search order: the error first, smallest value first, then the breaks from
    % left to right. The best error is small compared with the number of
    % elements, so trying error values in turn with the breaks narrowed to
    % them finds the optimum far sooner than improving a first arbitrary
    % split step by step.
    append([[Error], Breaks, Sizes], Vars).

% Sizes of the groups after the first: the gap to the previous break, and the
% rest of the N elements after the final break.
sizes_between_breaks([Previous], [Last], N) :- !,
    Last #= N - Previous.
sizes_between_breaks([Previous, Next|Breaks], [Size|Sizes], N) :-
    Size #= Next - Previous,
    sizes_between_breaks([Next|Breaks], Sizes, N).

% Positions I such that the I-th element of the list equals the next one.
equal_neighbours([X, Y|Rest], I, Positions) :- !,
    Next is I + 1,
    (   X =:= Y
    ->  Positions = [I|Others]
    ;   Positions = Others
    ),
    equal_neighbours([Y|Rest], Next, Others).
equal_neighbours(_, _, []).

labeling_options([leftmost]).
