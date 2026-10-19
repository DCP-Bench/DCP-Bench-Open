% csplib_033_word_design (word design for DNA computing).
% Find a set S of num_words words of length n over the alphabet {A,C,G,T},
% coded 1=A, 2=C, 3=G, 4=T. Output: words, a num_words x n array of codes.
% The Watson-Crick complement swaps A<->T (1<->4) and C<->G (2<->3), so comp(v) = 5 - v.

:- lib(ic).

model(Instance, Vars, [words-Rows], none) :-
    memberchk(n-N, Instance),
    memberchk(num_words-M, Instance),
    length(Rows, M),
    % Each word is a row of n letters, each letter in 1..4.
    % Each word has 4 symbols from {C,G}: exactly 4 positions with letter 2 or 3.
    ( foreach(Row, Rows), param(N) do
        length(Row, N),
        Row :: 1..4,
        ( foreach(V, Row), foreach(B, Bs) do B #= (V #= 2) + (V #= 3) ),
        sum(Bs) #= 4
    ),
    flatten(Rows, Vars),
    % Each pair of distinct words in S differ in at least 4 positions.
    distinct_words_differ(Rows),
    % Each pair of words x and y in S (x and y may be identical) are such that
    % x^R and y^C differ in at least 4 positions: the reverse of x and the
    % Watson-Crick complement of y.
    ( foreach(X, Rows), param(Rows) do
        ( foreach(Y, Rows), param(X) do reverse_complement_differ(X, Y) )
    ).

% Each pair of distinct words (earlier word, later word) differs in at least 4 positions.
distinct_words_differ([]).
distinct_words_differ([X|Xs]) :-
    ( foreach(Y, Xs), param(X) do hamming_at_least(X, Y, 4) ),
    distinct_words_differ(Xs).

% Two words of equal length differ in at least K positions.
hamming_at_least(X, Y, K) :-
    ( foreach(A, X), foreach(B, Y), foreach(D, Ds) do D #= (A #\= B) ),
    sum(Ds) #>= K.

% The reverse of x and the complement of y differ in at least 4 positions.
reverse_complement_differ(X, Y) :-
    reverse(X, RX),
    ( foreach(A, RX), foreach(B, Y), foreach(D, Ds) do D #= (A #\= 5 - B) ),
    sum(Ds) #>= 4.

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
