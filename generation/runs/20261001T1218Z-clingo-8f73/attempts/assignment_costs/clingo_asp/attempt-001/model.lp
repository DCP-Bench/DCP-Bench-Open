% Assignment with costs: give each task to one person so that the total cost is smallest. Every
% task must be assigned, but not every person has to get a task and nobody gets two.
% Instance facts: cost(I, J, C): doing task I by person J costs C (rows are tasks, columns people).
task(I) :- cost(I,_,_).
person(J) :- cost(_,J,_).

% assign(I, J): task I is done by person J. Each task is assigned to exactly one person.
1 { assign(I,J) : person(J) } 1 :- task(I).

% A person does at most one task.
:- person(J), #count { I : assign(I,J) } > 1.

% The total cost of the assignments, which is to be minimised.
#minimize { C,I,J : assign(I,J), cost(I,J,C) }.

% x(I, J, true/false): whether task I is assigned to person J.
x(I,J,true) :- assign(I,J).
x(I,J,false) :- task(I), person(J), not assign(I,J).

#show x/3.
