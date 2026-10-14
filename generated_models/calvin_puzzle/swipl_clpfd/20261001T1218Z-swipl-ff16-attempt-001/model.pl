:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(pairs)).
:- use_module(library(yall)).

% Calvin puzzle: fill an n x n grid with the numbers 1..n*n, each once, so that
% every number after the first sits a fixed jump away from the one before:
% either exactly three squares along a row or a column (two squares in
% between), or exactly two squares along both a row and a column, which is
% diagonal (one square in between).
model(Instance, Choices, [x-Rows]) :-
    N = Instance.n,                         % size of the grid
    Squares is N * N,
    Dummy is Squares + 1,                   % an extra node, explained below
    numlist(1, Squares, SquareIds),

    % Square (i, j), counted from 0, is node i*N + j + 1. Filling the grid in
    % sequence is a path through all squares, which is written as a circuit
    % through the squares and one extra node: the extra node is followed by the
    % square holding 1 and comes after the square holding n*n.
    % Successors[v] is the node visited after node v: a square a jump away, or
    % the extra node when v is the square holding n*n; the extra node leads to
    % any square.
    maplist(jumps(N), SquareIds, Moves),

    % How the search picks a successor: Choices[v] is a place in the list of
    % nodes that can follow v. The list puts the squares with the fewest jumps
    % first (they are the hardest to reach later, so they are best visited
    % early) and the extra node last. Trying small places first follows this
    % rule.
    maplist({Moves, Dummy}/[Targets, Candidates]>>candidates(Moves, Targets, Dummy, Candidates),
            Moves, SquareCandidates),
    numlist(1, Squares, AnySquare),
    candidates(Moves, AnySquare, none, StartCandidates),
    append(SquareCandidates, [StartCandidates], AllCandidates),
    maplist([Candidates, Choice, Next]>>
                (length(Candidates, Count), Choice in 1..Count,
                 element(Choice, Candidates, Next)),
            AllCandidates, Choices, Successors),
    % every node is left once, entered once, and the path closes into a
    % single circuit; this also means every square is visited once
    circuit(Successors),

    % Rows[i][j] is the number in row i, column j.
    length(Rows, N),
    maplist({N}/[Row]>>length(Row, N), Rows),
    append(Rows, Numbers),
    Numbers ins 1..Squares,
    % the numbers follow the path: the extra node counts as 0, so the first
    % square gets 1, and every jump to a square adds one. The numbers are
    % determined by Successors and are not labelled.
    append(Numbers, [0], AllNumbers),
    maplist({AllNumbers, Dummy}/[Next, Number]>>number_step(AllNumbers, Dummy, Next, Number),
            Successors, AllNumbers).

% candidates(+Moves, +Targets, +Dummy, -Candidates): the nodes in Targets ordered
% by how few jumps they have, fewest first, followed by Dummy (unless it is
% none).
candidates(Moves, Targets, Dummy, Candidates) :-
    maplist({Moves}/[Target, Count-Target]>>(nth1(Target, Moves, Onward), length(Onward, Count)),
            Targets, Counted),
    keysort(Counted, Sorted),
    pairs_values(Sorted, Ordered),
    (   Dummy == none
    ->  Candidates = Ordered
    ;   append(Ordered, [Dummy], Candidates)
    ).

% number_step(+AllNumbers, +Dummy, +Next, +Number): the node Next follows a node
% numbered Number; unless it is the extra node it is numbered one higher.
number_step(AllNumbers, Dummy, Next, Number) :-
    element(Next, AllNumbers, NextNumber),
    (Next #\= Dummy) #==> (NextNumber #= Number + 1).

% jumps(+N, +Square, -Targets): the squares of an N x N grid reached from Square
% by one jump. The jumps belong to the puzzle: three squares along a row or
% column, or two squares along both.
jumps(N, Square, Targets) :-
    I is (Square - 1) // N,
    J is (Square - 1) mod N,
    findall(Target,
            (   member([DI, DJ],
                       [[3, 0], [-3, 0], [0, 3], [0, -3], [2, 2], [2, -2], [-2, 2], [-2, -2]]),
                I2 is I + DI, J2 is J + DJ,
                I2 >= 0, I2 < N, J2 >= 0, J2 < N,
                Target is I2 * N + J2 + 1
            ),
            Targets).
