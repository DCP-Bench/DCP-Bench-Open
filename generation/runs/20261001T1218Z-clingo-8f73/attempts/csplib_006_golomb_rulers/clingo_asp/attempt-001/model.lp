% Golomb ruler: place size marks at integer positions, the first at 0, so that all the
% differences between two marks are distinct; the length of the ruler (the position of the last
% mark) is to be as small as possible.
% Instance facts: size(S): the number of marks. Positions lie between 0 and size * size, the
% bound the problem gives for the marks.
position(0..S*S) :- size(S).

% mark(P): there is a mark at position P. The first mark is at 0 and there are size marks in
% all. Naming the positions that carry a mark (rather than the position of the I-th mark)
% already makes the marks distinct and increasing.
mark(0).
{ mark(P) } :- position(P), P > 0.
:- size(S), S != #count { P : mark(P) }.

% Golomb constraint: every distance D is the difference of at most one pair of marks.
:- size(S), D = 1..S*S, #count { P : mark(P), mark(P + D) } > 1.

% marks(I, P): the I-th mark, counted from 0 in increasing order, is at position P.
marks(I,P) :- mark(P), I = #count { Q : mark(Q), Q < P }.

% The length of the ruler is the position of its last mark; it is to be minimised.
length(L) :- mark(L), #count { Q : mark(Q), Q > L } == 0.
#minimize { L : length(L) }.

#show marks/2.
#show length/1.
