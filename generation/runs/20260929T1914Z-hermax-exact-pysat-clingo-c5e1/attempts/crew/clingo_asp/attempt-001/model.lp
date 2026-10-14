% Crew assignment: staff each flight with cabin crew from a pool of flight
% attendants. A flight needs a given number of crew, of whom certain numbers
% must be stewards, hostesses and speakers of French, Spanish and German, and
% an attendant must have the two flights after an attended flight off.
% attributes(P, A, V): person P has attribute A (0 steward, 1 hostess, 2 French,
% 3 Spanish, 4 German) when V is 1. required_crew(F, K, N): flight F needs N
% people for K = 0 (the crew size) and N with attribute K - 1 for K = 1..5.
flight(F) :- required_crew(F,_,_).
person(P) :- attributes(P,_,_).

% works(F, P): person P works on flight F; crew/3 reports that as 1 or 0.
{ works(F,P) } :- flight(F), person(P).
crew(F,P,1) :- works(F,P).
crew(F,P,0) :- flight(F), person(P), not works(F,P).

% The flight has exactly the number of crew members it needs ...
:- required_crew(F,0,N), N != #count { P : works(F,P) }.
% ... and at least the required number of people with each attribute.
:- required_crew(F,K,N), K >= 1, N > #count { P : works(F,P), attributes(P,K-1,1) }.

% After a flight a person has the next two flights off.
:- works(F,P), works(F+1,P).
:- works(F,P), works(F+2,P).

#show crew/3.
