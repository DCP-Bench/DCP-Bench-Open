% N queens: one queen per row, no two sharing a column or a diagonal.
row(0..N-1) :- n(N).
column(1..N) :- n(N).

% Exactly one column per row.
1 { queens(R,C) : column(C) } 1 :- row(R).

% No shared column, and no shared diagonal.
:- queens(R1,C), queens(R2,C), R1 < R2.
:- queens(R1,C1), queens(R2,C2), R1 < R2, R2 - R1 == |C2 - C1|.

#show queens/2.
