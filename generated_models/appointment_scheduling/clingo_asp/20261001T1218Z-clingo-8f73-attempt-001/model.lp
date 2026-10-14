% Appointment scheduling: give each person one of the interview slots, using every slot once
% and only a slot in which that person is free.
% Instance facts: m(I, J, B): B is 1 when person I is free in slot J and 0 when busy.
person(I) :- m(I,_,_).
slot(J) :- m(_,J,_).

% assigned(I, J): person I is given slot J. Each person gets exactly one slot.
1 { assigned(I,J) : slot(J) } 1 :- person(I).

% Each slot is given to exactly one person.
1 { assigned(I,J) : person(I) } 1 :- slot(J).

% A person can only be given a slot in which they are free.
:- assigned(I,J), m(I,J,0).

% x(I, J, true) when person I is assigned to slot J, x(I, J, false) otherwise.
x(I,J,true) :- assigned(I,J).
x(I,J,false) :- person(I), slot(J), not assigned(I,J).

#show x/3.
