% Discrete tomography: reconstruct a 0/1 picture from its row and column sums.
row(I) :- row_sums(I,_).
col(J) :- col_sums(J,_).

{ matrix(I,J,1) } :- row(I), col(J).
matrix(I,J,0) :- row(I), col(J), not matrix(I,J,1).

filled_row(I,K) :- row(I), K = #count { J : matrix(I,J,1) }.
:- row_sums(I,S), filled_row(I,K), K != S.

filled_col(J,K) :- col(J), K = #count { I : matrix(I,J,1) }.
:- col_sums(J,S), filled_col(J,K), K != S.

#show matrix/3.
