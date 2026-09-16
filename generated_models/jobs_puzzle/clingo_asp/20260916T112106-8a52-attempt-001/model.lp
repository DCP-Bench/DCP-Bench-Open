% Jobs puzzle: four people hold eight jobs, two each. Every value is the index
% of the person doing that job.
person(0..3).

1 { chef(P) : person(P) } 1.
1 { guard(P) : person(P) } 1.
1 { nurse(P) : person(P) } 1.
1 { clerk(P) : person(P) } 1.
1 { police_officer(P) : person(P) } 1.
1 { teacher(P) : person(P) } 1.
1 { actor(P) : person(P) } 1.
1 { boxer(P) : person(P) } 1.

holds(chef,P) :- chef(P).
holds(guard,P) :- guard(P).
holds(nurse,P) :- nurse(P).
holds(clerk,P) :- clerk(P).
holds(police,P) :- police_officer(P).
holds(teacher,P) :- teacher(P).
holds(actor,P) :- actor(P).
holds(boxer,P) :- boxer(P).

% Each person holds exactly two jobs.
:- person(P), not 2 = #count { J : holds(J,P) }.

% 1. The nurse is not the teacher, police officer or clerk.
:- nurse(P), teacher(P).
:- nurse(P), police_officer(P).
:- nurse(P), clerk(P).
% 2. The clerk is not the chef.
:- clerk(P), chef(P).
% 3. Person 0 is not the boxer.
:- boxer(0).
% 4. Person 3 is not the teacher, police officer or nurse.
:- teacher(3).
:- police_officer(3).
:- nurse(3).
% 5. Person 0, the chef and the police officer are three different people.
:- chef(0).
:- police_officer(0).
:- chef(P), police_officer(P).

#show chef/1.
#show guard/1.
#show nurse/1.
#show clerk/1.
#show police_officer/1.
#show teacher/1.
#show actor/1.
#show boxer/1.
