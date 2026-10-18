% Jobs puzzle: four people hold eight different jobs (chef, guard, nurse, clerk,
% police officer, teacher, actor, boxer). Each person holds exactly two jobs.
% The output gives, for each job, the index (0-3) of the person who holds it.

:- lib(ic).
:- lib(ic_global).

model(_Instance, Vars, Outputs) :-
    Vars = [Chef, Guard, Nurse, Clerk, Police, Teacher, Actor, Boxer],
    Vars :: 0..3,

    % Each person holds exactly two jobs.
    ( for(P, 0, 3), param(Vars) do
        occurrences(P, Vars, 2)
    ),

    % Clue 1: The nurse is not a teacher, police officer, or clerk.
    Nurse #\= Teacher,
    Nurse #\= Police,
    Nurse #\= Clerk,

    % Clue 2: The clerk is not the chef.
    Clerk #\= Chef,

    % Clue 3: Person 0 is not the boxer.
    Boxer #\= 0,

    % Clue 4: Person 3 is not the teacher, police officer, or nurse.
    Teacher #\= 3,
    Police #\= 3,
    Nurse #\= 3,

    % Clue 5: Person 0, the chef, and the police officer went golfing together.
    Chef #= 0,
    Police #= 0,

    Outputs = [chef-Chef, guard-Guard, nurse-Nurse, clerk-Clerk,
               police_officer-Police, teacher-Teacher, actor-Actor, boxer-Boxer].
