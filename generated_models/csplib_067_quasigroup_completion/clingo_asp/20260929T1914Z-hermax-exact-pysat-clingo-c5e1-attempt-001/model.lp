% Quasigroup completion: fill the empty cells of a partially filled N x N grid
% so that every row and every column contains each of 1..N exactly once (a
% Latin square).
index(0..N-1) :- n(N).
number(1..N) :- n(N).

% Every cell holds exactly one number.
1 { puzzle(I,J,V) : number(V) } 1 :- index(I), index(J).

% The given cells keep their value (0 marks an empty cell).
:- start(I,J,V), V != 0, not puzzle(I,J,V).

% Each row and each column holds different numbers.
:- puzzle(I,J1,V), puzzle(I,J2,V), J1 < J2.
:- puzzle(I1,J,V), puzzle(I2,J,V), I1 < I2.

#show puzzle/3.
