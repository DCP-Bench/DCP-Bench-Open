:- use_module(library(clpfd)).

% Jobs puzzle: four people (numbered 0 to 3) hold eight different jobs, two
% jobs each: chef, guard, nurse, clerk, police officer, teacher, actor, boxer.
% Five clues restrict who holds what; find the person who holds each job. The
% problem has no instance data; the numbers of people and jobs are the ones in
% the statement. Each output is the person (0..3) holding that job.
model(_Instance, Vars,
      [chef-Chef, guard-Guard, nurse-Nurse, clerk-Clerk,
       police_officer-PoliceOfficer, teacher-Teacher, actor-Actor, boxer-Boxer]) :-
    Vars = [Chef, Guard, Nurse, Clerk, PoliceOfficer, Teacher, Actor, Boxer],
    Vars ins 0..3,

    % each person holds exactly two jobs
    global_cardinality(Vars, [0-2, 1-2, 2-2, 3-2]),

    % 1. The nurse is not a teacher, police officer or clerk.
    Nurse #\= Teacher,
    Nurse #\= PoliceOfficer,
    Nurse #\= Clerk,

    % 2. The clerk is not the chef.
    Clerk #\= Chef,

    % 3. Person 0 is not the boxer.
    Boxer #\= 0,

    % 4. Person 3 is not the teacher, police officer or nurse.
    Teacher #\= 3,
    PoliceOfficer #\= 3,
    Nurse #\= 3,

    % 5. Person 0, the chef and the police officer went golfing together, so
    %    they are three different people.
    Chef #\= 0,
    PoliceOfficer #\= 0,
    Chef #\= PoliceOfficer.
