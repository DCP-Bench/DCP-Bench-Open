% Kidney exchange: n people wait for a kidney. Person i can donate to the people listed for i.
% Choose who donates to whom so that everyone who gives a kidney also receives one, nobody gives
% or receives more than one, and as many transplants as possible happen.
% Instance facts: num_people(N); compatible(I,K,J): J is the K-th person (numbered from 1) to
% whom person I (numbered from 0) can donate. A person with an empty list has no facts.
person(0..N-1) :- num_people(N).

% can_donate(I,J): person I can donate to person J (both numbered from 0; the list uses numbering from 1).
can_donate(I,J-1) :- compatible(I,_,J).

% donates(I,J): person I donates to person J, which is only possible for a compatible pair.
{ donates(I,J) : can_donate(I,J) } :- person(I).

% Each person donates to at most one person and receives from at most one person.
:- person(I), #count { J : donates(I,J) } > 1.
:- person(J), #count { I : donates(I,J) } > 1.

% Anyone who gives a kidney must receive one.
:- donates(I,_), not donates(_,I).

% Maximise the number of transplants.
#maximize { 1,I,J : donates(I,J) }.

% transplants(I,J,true/false): whether person I donates to person J.
transplants(I,J,true)  :- donates(I,J).
transplants(I,J,false) :- person(I), person(J), not donates(I,J).

#show transplants/3.
