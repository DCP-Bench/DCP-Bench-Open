% Job shop scheduling: every job is a sequence of tasks, each to be processed on a given machine for
% a given time. A task cannot start before the previous task of its job has finished, a machine
% processes one task at a time, and a task runs to completion once started. Schedule all tasks so
% that the makespan (the time at which all jobs are finished) is as small as possible.
% Instance facts: jobs_data(J, K, 0, M) and jobs_data(J, K, 1, D): the K-th task of job J runs
% on machine M and takes D time units.
task(t(J,K)) :- jobs_data(J,K,0,_).
machine_of(t(J,K),M) :- jobs_data(J,K,0,M).
dur(t(J,K),D) :- jobs_data(J,K,1,D).

% horizon: the sum of all durations. No schedule without idle gaps is longer, so a start time
% never has to be later than this (the problem uses it as the largest time).
horizon(H) :- H = #sum { D,A : dur(A,D) }.

% prec(A, B): task A is processed before task B on their common machine. Of two tasks on the same
% machine one comes first (a machine does one task at a time).
same_machine(A,B) :- machine_of(A,M), machine_of(B,M), A < B.
1 { prec(A,B); prec(B,A) } 1 :- same_machine(A,B).

% follows(A, B): task B cannot start before task A has finished. This holds for consecutive tasks
% of a job, and for tasks ordered on a machine.
follows(t(J,K),t(J,K + 1)) :- task(t(J,K)), task(t(J,K + 1)).
follows(A,B) :- prec(A,B).

% ge(A, T): task A starts at time T or later. A task is pushed later by the duration of every
% task that has to finish before it starts, along any chain of such tasks. A chain that
% would run past the horizon belongs to a circular order of tasks (A before B before ... before A), which
% is no schedule, so it is forbidden. The thresholds are only listed where they are reached, so
% a task starts at its largest one.
ge(B,D) :- follows(A,B), dur(A,D), D > 0.
ge(B,T + D) :- ge(A,T), follows(A,B), dur(A,D), horizon(H), T + D <= H.
:- ge(A,T), dur(A,D), horizon(H), T + D > H.

% fin(T): the schedule is not finished before time T. A task ends at its start plus its duration.
% Not being finished before T implies not being finished before T - 1.
fin(T + D) :- ge(A,T), dur(A,D).
fin(D) :- dur(A,D), D > 0.
fin(T - 1) :- fin(T), T > 1.

% The makespan is at least the work of any machine and the length of any job, because a machine
% does one task at a time and a job runs its tasks one after another. This follows from the
% constraints above; stating it lets the search stop as soon as a schedule of that length is found.
machine_load(M,S) :- machine_of(_,M), S = #sum { D,A : machine_of(A,M), dur(A,D) }.
job_length(J,S) :- jobs_data(J,_,_,_), S = #sum { D,K : jobs_data(J,K,1,D) }.
lower_bound(L) :- L = #max { S : machine_load(_,S) ; S : job_length(_,S) }.
fin(T) :- lower_bound(L), T = 1..L.

% The makespan is the largest T with fin(T). Minimise it.
makespan(T) :- fin(T), not fin(T + 1).
#minimize { 1,T : fin(T) }.

% Which schedule gives the makespan is not part of the answer, so solutions are projected onto
% makespan.
#project makespan/1.
#show makespan/1.
