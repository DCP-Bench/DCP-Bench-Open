% Magic square: fill an n x n grid with the different integers 1..n^2 so that
% every row, every column and both diagonals add up to the same sum.
cell(0..N-1) :- n(N).
value(1..N*N) :- n(N).
magic(N * (N * N + 1) / 2) :- n(N).  % the sum every line has to reach

% Every cell holds exactly one number, and no number is used twice.
1 { square(I,J,V) : value(V) } 1 :- cell(I), cell(J).
:- square(I,J,V), square(K,L,V), (I,J) < (K,L).

% Each row, each column and both diagonals add up to the magic sum.
:- magic(S), cell(I), S != #sum { V,J : square(I,J,V) }.
:- magic(S), cell(J), S != #sum { V,I : square(I,J,V) }.
:- magic(S), S != #sum { V,I : square(I,I,V) }.
:- magic(S), n(N), S != #sum { V,I : square(I,J,V), J == N - 1 - I }.

#show square/3.
