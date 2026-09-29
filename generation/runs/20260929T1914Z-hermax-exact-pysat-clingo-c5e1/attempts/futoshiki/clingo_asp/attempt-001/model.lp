% Futoshiki: fill an n x n grid with 1..n so that every row and column has each
% number once, some cells are given, and the listed "less than" signs between
% neighbouring cells hold.
size(N) :- N = #count { R : values(R,0,_) }.
index(0..N-1) :- size(N).
number(1..N) :- size(N).

% Every cell holds exactly one number.
1 { grid(R,C,V) : number(V) } 1 :- index(R), index(C).

% The given numbers are fixed (0 means empty).
:- values(R,C,V), V > 0, not grid(R,C,V).

% Every row and every column holds different numbers.
:- grid(R,C1,V), grid(R,C2,V), C1 < C2.
:- grid(R1,C,V), grid(R2,C,V), R1 < R2.

% Each inequality sign lt(K, ...) = [i1, j1, i2, j2]: the first cell is smaller than
% the second (the coordinates in the data start at 1).
:- lt(K,0,I1), lt(K,1,J1), lt(K,2,I2), lt(K,3,J2),
   grid(I1-1,J1-1,V1), grid(I2-1,J2-1,V2), V1 >= V2.

#show grid/3.
