% Finding celebrities: among the guests of a party, find the celebrities. A celebrity is known by
% everybody at the party and knows only other celebrities; at least one celebrity is present.
% Instance facts: graph(I, J, V): V is 1 when guest I knows guest J, and 0 otherwise.
person(I) :- graph(I,_,_).
total(N) :- N = #count { I : person(I) }.

% celebrity(I): guest I is a celebrity.
{ celebrity(I) : person(I) }.

% num_celebrities: how many celebrities there are; there is at least one.
num_celebrities(C) :- C = #count { I : celebrity(I) }.
:- num_celebrities(C), C < 1.

% known_by_all(I): everybody knows guest I (the column of the matrix for I adds up to the
% number of guests; the matrix counts a guest as knowing themselves).
known_by_all(I) :- person(I), total(N), N = #sum { V,J : graph(J,I,V) }.

% knows_celebrities(I): guest I knows exactly as many guests as there are celebrities (the
% row of the matrix for I adds up to the number of celebrities).
knows_celebrities(I) :- person(I), num_celebrities(C), C = #sum { V,J : graph(I,J,V) }.

% A guest is a celebrity exactly when everybody knows them and they know only celebrities.
:- celebrity(I), not known_by_all(I).
:- celebrity(I), not knows_celebrities(I).
:- known_by_all(I), knows_celebrities(I), not celebrity(I).

% celebrities(I, true/false): whether guest I is a celebrity.
celebrities(I,true) :- celebrity(I).
celebrities(I,false) :- person(I), not celebrity(I).

#show celebrities/2.
