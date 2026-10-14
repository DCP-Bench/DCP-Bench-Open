% Word design: find num_words words of length n over the alphabet {A, C, G, T} (coded 1, 2, 3, 4)
% such that every word has exactly 4 letters from {C, G}, any two different words differ in at
% least 4 positions, and for any two words x and y (possibly the same word) the reverse of x
% and the Watson-Crick complement of y differ in at least 4 positions.
% Instance facts: n(N): the length of each word; num_words(M): how many words to find.
% The figure 4 in the three properties is fixed by the problem statement, not by the instance.
word(0..M-1) :- num_words(M).
position(0..N-1) :- n(N).

% words(I, J, L): the J-th letter of word I is L (1 = A, 2 = C, 3 = G, 4 = T). Every position
% of every word holds exactly one letter.
1 { words(I,J,1..4) } 1 :- word(I), position(J).

% Each word has exactly 4 symbols from {C, G}.
strong(I,J) :- words(I,J,2).
strong(I,J) :- words(I,J,3).
:- word(I), #count { J : strong(I,J) } != 4.

% Each pair of distinct words differs in at least 4 positions, that is, they agree in at most
% n - 4 positions.
:- word(I1), word(I2), I1 < I2, n(N), #count { J : words(I1,J,L), words(I2,J,L) } > N - 4.

% For every pair of words x and y (x and y may be the same word), the reverse of x and the
% complement of y differ in at least 4 positions. The complement of a letter L is 5 - L
% (A and T swap, C and G swap) and position J of the reverse of x holds letter x[N-1-J].
:- word(X), word(Y), n(N),
   #count { J : words(Y,J,M), words(X,K,L), K = N - 1 - J, L + M = 5 } > N - 4.

#show words/3.
