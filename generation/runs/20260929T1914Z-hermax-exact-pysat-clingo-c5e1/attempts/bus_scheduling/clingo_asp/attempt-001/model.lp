% Bus scheduling: the day is cut into equal time slots and a bus works two
% consecutive slots. Choose how many buses start in each slot so that every
% slot's demand is met with as few buses as possible.
% demands(I, D): D buses are needed in slot I.
slot(I) :- demands(I,_).
slots(N) :- N = #count { I : slot(I) }.
total(T) :- T = #sum { D,I : demands(I,D) }.

% x(I, B): B buses start working in slot I.
1 { x(I,B) : B = 0..T } 1 :- slot(I), total(T).

% A bus covers its starting slot and the next one (the day wraps around), so slot
% I+1 is served by the buses starting in slots I and I+1.
:- slot(I), slots(N), J = (I + 1) \ N, x(I,A), x(J,B), demands(J,D), A + B < D.

% Use as few buses as possible.
#minimize { B,I : x(I,B) }.

#show x/2.
