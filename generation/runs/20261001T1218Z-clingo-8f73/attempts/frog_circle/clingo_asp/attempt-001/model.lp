% Frog circle: cards numbered 1 to n are arranged in a circle. A frog starts on card 1 and from
% a card with number k jumps k places clockwise. Arrange the cards so that the frog lands on
% every card.
% Instance facts: n(N), the number of cards.
position(0..N-1) :- n(N).
card(1..N) :- n(N).

% x(P, V): the card at position P (0..N-1 around the circle) is V. Each position holds one
% card and each card is used once.
1 { x(P,V) : card(V) } 1 :- position(P).
1 { x(P,V) : position(P) } 1 :- card(V).

% The frog starts on card 1, which is at position 0.
:- not x(0,1).

% visit(I, P): the frog is at position P after I jumps. The next position is the current one
% plus the number on the card there, counted around the circle.
visit(0,0).
visit(I+1,(P + V) \ N) :- visit(I,P), x(P,V), n(N), I + 1 < N.

% The frog must be on every card, so the positions it visits are all different.
:- visit(I,P), visit(J,P), I < J.

#show x/2.
