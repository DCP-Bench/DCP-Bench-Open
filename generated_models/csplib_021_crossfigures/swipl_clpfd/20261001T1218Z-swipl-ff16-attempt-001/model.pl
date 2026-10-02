:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Crossfigure: a crossword whose answers are numbers. Fill a 9 x 9 grid with
% digits so that every across and down answer satisfies its clue, which ties it
% to other answers, fixes it, or says it is a square or a prime.
model(_Instance, Cells, ['M'-Rows]) :-
    % The grid and the clues belong to the problem (there are no instance
    % fields). b is a black box, w a cell holding a digit.
    Layout = [[w, w, w, w, b, w, w, w, w],
              [w, w, b, w, w, w, b, w, w],
              [w, b, w, w, b, w, w, b, w],
              [w, w, w, w, b, w, w, w, w],
              [b, w, b, b, b, b, b, w, b],
              [w, w, w, w, b, w, w, w, w],
              [w, b, w, w, b, w, w, b, w],
              [w, w, b, w, w, w, b, w, w],
              [w, w, w, w, b, w, w, w, w]],
    Max = 9999,                             % every answer has at most 4 digits

    % Rows[i][j] is the digit in row i, column j (counted from 1); a black box
    % holds 0, which is how the answer prints it.
    maplist(layout_row, Layout, Rows),
    append(Rows, Cells),
    transpose(Rows, Columns),

    % The answers: A<k> is the across answer numbered k, D<k> the down answer.
    Numbers = [A1, A4, A7, A8, A9, A10, A11, A13, A15, A17, A20, A23, A24, A25, A27, A28, A29, A30,
               D1, D2, D3, D4, D5, D6, D10, D12, D14, D16, D17, D18, D19, D20, D21, D22, D26, D28],
    Numbers ins 0..Max,

    % Where each answer is written: its number of digits and the row and column
    % of its first digit. An answer is the number the digits spell out.
    across(Rows, A1, 4, 1, 1),   across(Rows, A4, 4, 1, 6),   across(Rows, A7, 2, 2, 1),
    across(Rows, A8, 3, 2, 4),   across(Rows, A9, 2, 2, 8),   across(Rows, A10, 2, 3, 3),
    across(Rows, A11, 2, 3, 6),  across(Rows, A13, 4, 4, 1),  across(Rows, A15, 4, 4, 6),
    across(Rows, A17, 4, 6, 1),  across(Rows, A20, 4, 6, 6),  across(Rows, A23, 2, 7, 3),
    across(Rows, A24, 2, 7, 6),  across(Rows, A25, 2, 8, 1),  across(Rows, A27, 3, 8, 4),
    across(Rows, A28, 2, 8, 8),  across(Rows, A29, 4, 9, 1),  across(Rows, A30, 4, 9, 6),
    down(Columns, D1, 4, 1, 1),  down(Columns, D2, 2, 1, 2),  down(Columns, D3, 4, 1, 4),
    down(Columns, D4, 4, 1, 6),  down(Columns, D5, 2, 1, 8),  down(Columns, D6, 4, 1, 9),
    down(Columns, D10, 2, 3, 3), down(Columns, D12, 2, 3, 7), down(Columns, D14, 3, 4, 2),
    down(Columns, D16, 3, 4, 8), down(Columns, D17, 4, 6, 1), down(Columns, D18, 2, 6, 3),
    down(Columns, D19, 4, 6, 4), down(Columns, D20, 4, 6, 6), down(Columns, D21, 2, 6, 7),
    down(Columns, D22, 4, 6, 9), down(Columns, D26, 2, 8, 2), down(Columns, D28, 2, 8, 8),

    % Squares and primes below the largest answer, for the clues that ask for
    % one. Each division clue is posted as a multiplication.
    findall(Square, (between(1, 100, Root), Square is Root * Root, Square =< Max), Squares),
    findall(Prime, (between(2, Max, Prime), is_prime(Prime)), Primes),
    list_to_domain(Squares, SquareDomain),
    list_to_domain(Primes, PrimeDomain),

    % Across clues
    A1 #= 2 * A27,                % 1  27 across times two
    A4 #= D4 + 71,                % 4  4 down plus seventy-one
    A7 #= D18 + 4,                % 7  18 down plus four
    16 * A8 #= D6,                % 8  6 down divided by sixteen
    A9 #= D2 - 18,                % 9  2 down minus eighteen
    12 * A10 #= 6 * 144,          % 10 dozen in six gross
    A11 #= D5 - 70,               % 11 5 down minus seventy
    A13 #= D26 * A23,             % 13 26 down times 23 across
    A15 #= D6 - 350,              % 15 6 down minus 350
    A17 #= A25 * A23,             % 17 25 across times 23 across
    A20 in SquareDomain,          % 20 a square number
    A23 in PrimeDomain,           % 23 a prime number
    A24 in SquareDomain,          % 24 a square number
    17 * A25 #= A20,              % 25 20 across divided by seventeen
    4 * A27 #= D6,                % 27 6 down divided by four
    A28 #= 4 * 12,                % 28 four dozen
    A29 #= 7 * 144,               % 29 seven gross
    A30 #= D22 + 450,             % 30 22 down plus 450

    % Down clues
    D1 #= A1 + 27,                % 1  1 across plus twenty-seven
    D2 #= 5 * 12,                 % 2  five dozen
    D3 #= A30 + 888,              % 3  30 across plus 888
    D4 #= 2 * A17,                % 4  two times 17 across
    12 * D5 #= A29,               % 5  29 across divided by twelve
    D6 #= A28 * A23,              % 6  28 across times 23 across
    D10 #= A10 + 4,               % 10 10 across plus four
    D12 #= A24 * 3,               % 12 three times 24 across
    16 * D14 #= A13,              % 14 13 across divided by sixteen
    D16 #= 15 * D28,              % 16 28 down times fifteen
    D17 #= A13 - 399,             % 17 13 across minus 399
    18 * D18 #= A29,              % 18 29 across divided by eighteen
    D19 #= D22 - 94,              % 19 22 down minus ninety-four
    D20 #= A20 - 9,               % 20 20 across minus nine
    D21 #= A25 - 52,              % 21 25 across minus fifty-two
    D22 #= 6 * D20,               % 22 20 down times six
    D26 #= 5 * A24,               % 26 five times 24 across
    D28 #= D21 + 27.              % 28 21 down plus twenty-seven

% layout_row(+Layout, -Row): a black box (b) holds 0, any other cell a digit.
layout_row(Layout, Row) :-
    maplist([Spec, Cell]>>(Spec == b -> Cell = 0 ; Cell in 0..9), Layout, Row).

% across(+Rows, ?Answer, +Length, +Row, +Col): Answer is the number spelled by the
% Length digits that start in row Row, column Col and run to the right.
across(Rows, Answer, Length, Row, Col) :-
    nth1(Row, Rows, Line),
    Skipped is Col - 1,
    length(Before, Skipped),
    append(Before, After, Line),
    length(Digits, Length),
    append(Digits, _, After),
    foldl([Digit, Value0, Value]>>(Value #= 10 * Value0 + Digit), Digits, 0, Answer).

% down(+Columns, ?Answer, +Length, +Row, +Col): the same, running downwards. Columns
% is the grid read column by column, so down is across on the transposed grid.
down(Columns, Answer, Length, Row, Col) :-
    across(Columns, Answer, Length, Col, Row).

% is_prime(+N): N is a prime number.
is_prime(N) :-
    N >= 2,
    Limit is floor(sqrt(N)),
    \+ ( between(2, Limit, Factor), N mod Factor =:= 0 ).

% list_to_domain(+Ints, -Domain): the finite domain holding exactly Ints.
list_to_domain([First|Rest], Domain) :-
    foldl([X, Domain0, Domain1]>>(Domain1 = Domain0 \/ X), Rest, First, Domain).
