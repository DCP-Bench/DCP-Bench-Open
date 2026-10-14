% Jobs puzzle: four people hold eight different jobs, two each, subject to
% clues about who is not what.
% The puzzle is fixed by the problem; the instance carries no data.
% chef(P), guard(P), ...: the job is held by person P, 0 to 3.
person(0..3).
1 { chef(P) : person(P) } 1.
1 { guard(P) : person(P) } 1.
1 { nurse(P) : person(P) } 1.
1 { clerk(P) : person(P) } 1.
1 { police_officer(P) : person(P) } 1.
1 { teacher(P) : person(P) } 1.
1 { actor(P) : person(P) } 1.
1 { boxer(P) : person(P) } 1.

% Every person holds exactly two jobs.
:- person(P), #count { chef : chef(P); guard : guard(P); nurse : nurse(P); clerk : clerk(P);
                       police_officer : police_officer(P); teacher : teacher(P);
                       actor : actor(P); boxer : boxer(P) } != 2.

% 1. The nurse is not the teacher, the police officer or the clerk.
:- nurse(P), teacher(P).
:- nurse(P), police_officer(P).
:- nurse(P), clerk(P).
% 2. The clerk is not the chef.
:- clerk(P), chef(P).
% 3. Person 0 is not the boxer.
:- boxer(0).
% 4. Person 3 is not the teacher, the police officer or the nurse.
:- teacher(3).
:- police_officer(3).
:- nurse(3).
% 5. Person 0, the chef and the police officer went golfing together, so they are
% three different people.
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
