% table/2, element/3, lex_le/2 and sorted/2 on a small route-of-three problem.
% Three stops A, B, C from 1..5; consecutive stops must be an allowed pair
% (a table), each stop has a cost (element/3), the cost vector is compared
% lexicographically with its mirror to cut symmetric answers.
:- lib(ic).
:- lib(ic_global).
:- lib(ic_mdd).                              % table/2
:- import alldifferent/1 from ic_global.

allowed([[1,2], [2,3], [3,1], [3,4], [4,5], [5,1], [2,5]]).
cost([4, 1, 3, 2, 5]).                       % cost of stop 1..5

stops([A,B,C]) :-
    [A,B,C] :: 1..5,
    allowed(T),
    table([[A,B]], T),                       % (A,B) is one of the rows of T
    table([[B,C]], T),
    alldifferent([A,B,C]),
    lex_le([A,B,C], [C,B,A]).                % A =< C breaks the mirror symmetry

main :-
    findall([A,B,C], (stops([A,B,C]), labeling([A,B,C])), All),
    length(All, N),
    printf("%d routes%n", [N]),
    ( foreach(R, All) do
        cost(Cs),
        R = [A,B,C],
        element(A, Cs, CA), element(B, Cs, CB), element(C, Cs, CC),
        Total is CA + CB + CC,               % all fixed here, so is/2 works
        printf("%w cost %d%n", [R, Total])
    ),
    % sorted/2: the second list is the first one, sorted
    Xs = [7, X2, 2, 9],
    X2 :: 3..8,
    sorted(Xs, Ys),
    Ys = [_, 3, _, _],                       % the second smallest value is 3
    labeling(Xs),
    printf("sorted: %w -> %w%n", [Xs, Ys]).
