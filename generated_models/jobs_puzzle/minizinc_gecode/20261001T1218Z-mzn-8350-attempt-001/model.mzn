% Jobs puzzle: four people hold eight different jobs (chef, guard, nurse, clerk,
% police officer, teacher, actor, boxer), each person exactly two of them. Clues
% about who cannot hold which job decide who holds what.
include "globals.mzn";

% The problem statement fixes these constants; the instance carries no data.
int: num_people = 4;               % people 0..3
int: num_jobs = 8;                 % eight different jobs

% the person (0..3) who holds each job
var 0..num_people - 1: chef;
var 0..num_people - 1: guard;
var 0..num_people - 1: nurse;
var 0..num_people - 1: clerk;
var 0..num_people - 1: police_officer;
var 0..num_people - 1: teacher;
var 0..num_people - 1: actor;
var 0..num_people - 1: boxer;
array[1..num_jobs] of var 0..num_people - 1: holder =
    [chef, guard, nurse, clerk, police_officer, teacher, actor, boxer];

% each person holds exactly two jobs
constraint global_cardinality(holder, [0, 1, 2, 3], [2, 2, 2, 2]);

% 1. the nurse is not a teacher, police officer or clerk
constraint nurse != teacher /\ nurse != police_officer /\ nurse != clerk;

% 2. the clerk is not the chef
constraint clerk != chef;

% 3. person 0 is not the boxer
constraint boxer != 0;

% 4. person 3 is not the teacher, police officer or nurse
constraint teacher != 3 /\ police_officer != 3 /\ nurse != 3;

% 5. person 0, the chef and the police officer went golfing together: they are three different people
constraint chef != 0 /\ police_officer != 0 /\ chef != police_officer;

solve satisfy;

output ["{\"chef\": ", show(chef), ", \"guard\": ", show(guard), ", \"nurse\": ", show(nurse),
        ", \"clerk\": ", show(clerk), ", \"police_officer\": ", show(police_officer),
        ", \"teacher\": ", show(teacher), ", \"actor\": ", show(actor),
        ", \"boxer\": ", show(boxer), "}"];
