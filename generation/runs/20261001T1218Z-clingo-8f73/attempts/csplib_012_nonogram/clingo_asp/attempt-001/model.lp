% Nonogram: shade squares of a grid so that, in every row and every column, the blocks of
% consecutive shaded squares have exactly the lengths given by that line's rule, in that
% order, with at least one unshaded square between two blocks.
% Instance facts: rows(R), cols(C); row_rules(I, K, L) and col_rules(J, K, L): the K-th entry
% of the rule of row I (column J) is L. A rule is padded with zeros, which are not blocks.
row(0..R-1) :- rows(R).
col(0..C-1) :- cols(C).

% The shaded blocks of a line, in the order of the rule: block(D, I, K, L) says the K-th
% entry of the rule of line I of direction D (r = row, c = column) is a block of length L.
block(r,I,K,L) :- row_rules(I,K,L), L > 0.
block(c,J,K,L) :- col_rules(J,K,L), L > 0.

% A row has as many squares as there are columns, and a column as many as there are rows.
squares(r,I,C) :- row(I), cols(C).
squares(c,J,R) :- col(J), rows(R).

% Space that the blocks before block K, and the blocks after it, need on the line: their
% lengths plus one gap square each.
before(D,I,K,S + N) :- block(D,I,K,_),
    S = #sum { L2,K2 : block(D,I,K2,L2), K2 < K },
    N = #count { K2 : block(D,I,K2,_), K2 < K }.
after(D,I,K,S + N) :- block(D,I,K,_),
    S = #sum { L2,K2 : block(D,I,K2,L2), K2 > K },
    N = #count { K2 : block(D,I,K2,_), K2 > K }.

% Each block starts at exactly one square. The start cannot be earlier than the space
% needed by the blocks before it, nor later than leaves room for the blocks after it; these
% bounds follow from the rule and keep the number of start atoms small.
1 { start(D,I,K,P) : P = B..N - L - A } 1 :-
    block(D,I,K,L), before(D,I,K,B), after(D,I,K,A), squares(D,I,N).

% Consecutive blocks of a line (K1 directly before K2, zero padding skipped).
between(D,I,K1,K2) :- block(D,I,K1,_), block(D,I,K2,_), block(D,I,K3,_), K1 < K3, K3 < K2.
next(D,I,K1,K2) :- block(D,I,K1,_), block(D,I,K2,_), K1 < K2, not between(D,I,K1,K2).

% A block is followed by an unshaded square before the next block starts.
:- next(D,I,K1,K2), start(D,I,K1,P1), block(D,I,K1,L1), start(D,I,K2,P2), P2 < P1 + L1 + 1.

% shaded(D, I, P): square P of line I of direction D is covered by one of its blocks.
shaded(D,I,P) :- start(D,I,K,S), block(D,I,K,L), P = S..S + L - 1.

% A square lies in a row and in a column; both must agree on whether it is shaded.
:- shaded(r,I,J), not shaded(c,J,I).
:- shaded(c,J,I), not shaded(r,I,J).

% board(I, J, 1) for a shaded square, board(I, J, 0) for an unshaded one.
board(I,J,1) :- shaded(r,I,J).
board(I,J,0) :- row(I), col(J), not shaded(r,I,J).

#show board/3.
