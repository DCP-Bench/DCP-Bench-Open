% Car selection: assign participants to cars, each participant to at most one car and each car
% to at most one participant, only to cars the participant is interested in, so that as many
% assignments as possible are made.
% Instance facts: possible_assignments(I, J, B): B is 1 when participant I is interested in car J.
participant(I) :- possible_assignments(I,_,_).
car(J) :- possible_assignments(_,J,_).

% assign(I, J): participant I gets car J, allowed only where the participant is interested.
{ assign(I,J) } :- possible_assignments(I,J,1).

% Each participant is assigned to at most one car.
:- participant(I), #count { J : assign(I,J) } > 1.

% Each car is assigned to at most one participant.
:- car(J), #count { I : assign(I,J) } > 1.

% As many assignments as possible.
#maximize { 1,I,J : assign(I,J) }.

% assignments(I, J, true/false): whether participant I is assigned to car J.
assignments(I,J,true) :- assign(I,J).
assignments(I,J,false) :- participant(I), car(J), not assign(I,J).

#show assignments/3.
