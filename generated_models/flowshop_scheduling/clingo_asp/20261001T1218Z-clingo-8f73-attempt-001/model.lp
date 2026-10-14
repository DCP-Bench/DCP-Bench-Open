% Flow shop scheduling: every job is processed on all machines in the same order, machine 1 first and
% machine M last. Jobs form a sequence, and each machine processes the jobs in that sequence, one
% at a time. Find the sequence of jobs that makes the makespan (the time at which all jobs are
% finished) as small as possible.
% Instance facts: jobs(I, _) numbers the jobs, machines(M, _) numbers the machines,
% process_time(J, M, D): job J takes D time units on machine M.
job(J) :- jobs(J,_).
machine(M) :- machines(M,_).
slot(K) :- job(K).

% sequence(K, J): the job J is the K-th job of the sequence, counted from 0. Every position holds
% one job and every job takes one position.
1 { sequence(K,J) : job(J) } 1 :- slot(K).
1 { sequence(K,J) : slot(K) } 1 :- job(J).

% ge(K, M, T): the K-th job of the sequence finishes on machine M at time T or later. A job starts
% on a machine once it has finished on the previous machine and once the previous job of the
% sequence has finished on this machine, so each of these two finishing times pushes this one
% later by the processing time. A job can always start at time 0. Finishing at T implies finishing
% at T - 1 or later, so the number of true ge atoms of a job and machine is its finishing time.
ge(K,M,D) :- sequence(K,J), process_time(J,M,D), D > 0.
ge(K,M,T + D) :- sequence(K,J), process_time(J,M,D), ge(K - 1,M,T).
ge(K,M,T + D) :- sequence(K,J), process_time(J,M,D), ge(K,M - 1,T).
ge(K,M,T - 1) :- ge(K,M,T), T > 1.

% The makespan is the time at which the last job of the sequence finishes on the last machine
% (the finishing times never decrease along the sequence or along the machines).
last_slot(K) :- K = #max { I : slot(I) }.
last_machine(M) :- M = #max { I : machine(I) }.
makespan(T) :- last_slot(K), last_machine(M), ge(K,M,T), not ge(K,M,T + 1).

% Minimise the makespan.
#minimize { 1,T : last_slot(K), last_machine(M), ge(K,M,T) }.

% Which sequence gives the makespan is not part of the answer, so solutions are projected onto makespan.
#project makespan/1.
#show makespan/1.
