idx(0..N-1) :- n(N).
mark(1..N) :- n(N).

% A permutation of the marks, one per position.
1 { costas(I,M) : mark(M) } 1 :- idx(I).
:- costas(I1,M), costas(I2,M), I1 < I2.

% Row L of the difference triangle holds costas[J] - costas[J-L-1] for J > L,
% and each row up to N-3 must have distinct entries.
:- n(N), L = 0..N-3, idx(J1), idx(J2), J1 < J2, J1 > L, J2 > L,
   costas(J1,A1), costas(J1-L-1,B1), costas(J2,A2), costas(J2-L-1,B2),
   A1 - B1 == A2 - B2.

#show costas/2.
