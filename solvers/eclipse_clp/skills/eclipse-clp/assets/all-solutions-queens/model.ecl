% N-queens, all solutions with findall/3. Qs[I] is the row of the queen in column I.
:- lib(ic).

queens(N, Qs) :-
    length(Qs, N),
    Qs :: 1..N,
    % no two queens in the same row or on a common diagonal
    ( fromto(Qs, [Q|Rest], Rest, []) do
        ( foreach(Q2, Rest), count(D, 1, _), param(Q) do
            Q #\= Q2,
            Q #\= Q2 + D,
            Q #\= Q2 - D
        )
    ),
    labeling(Qs).

main :-
    N = 8,
    findall(Qs, queens(N, Qs), All),       % copies are ground after labeling
    length(All, Count),
    printf("%d solutions for %d queens%n", [Count, N]),
    All = [First|_],
    printf("first: %w%n", [First]),
    % count only the solutions whose first queen (column 1) is in row 1
    findall(Qs, (member(Qs, All), Qs = [1|_]), Corner),
    length(Corner, CornerCount),
    printf("%d of them have the first queen in row 1%n", [CornerCount]).
