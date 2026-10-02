% Resource-constrained project scheduling: give every job a start time so that each job starts
% after all its predecessors have finished, the jobs running at any moment never need more of a
% resource than its capacity, and the last job to start (the makespan) starts as early as possible.
% Instance facts: durations_data(J,D); resource_needs_data(J,R,Q): job J uses Q of resource R while
% it runs; resource_capacities_data(R,C); successors_link_data(K,0,P) and (K,1,S): job S may start
% only after job P has finished.
job(J) :- durations_data(J,_).
resource(R) :- resource_capacities_data(R,_).
link(P,S) :- successors_link_data(K,0,P), successors_link_data(K,1,S).

% The reference bounds every start time by the total duration of all jobs (a dummy horizon).
horizon(H) :- H = #sum { D,J : durations_data(J,D) }.
longest(M) :- M = #max { D : durations_data(_,D) }.

% Start times use an order encoding: ge_s(J,T) holds when job J starts at time T or later.
% Unary threshold atoms make the precedence and capacity rules propagate strongly.
{ ge_s(J,T) : T = 1..H } :- job(J), horizon(H).
:- ge_s(J,T+1), not ge_s(J,T), T >= 1.

% start_time(J,T): job J starts at time T.
start_time(J,0) :- job(J), not ge_s(J,1).
start_time(J,T) :- ge_s(J,T), not ge_s(J,T+1).

% Precedence: a job starts no earlier than the finish of each predecessor, start(S) >= start(P) + duration(P).
% In order encoding: if P starts at T or later, S starts at T + duration(P) or later. An atom that
% does not exist stands for a start time beyond the horizon.
:- link(P,S), durations_data(P,D), D >= 1, not ge_s(S,D).
:- link(P,S), durations_data(P,D), ge_s(P,T), not ge_s(S,T+D).

% runs(J,T): job J is running at time T, that is, it started at some time in T-D+1..T.
runs(J,T) :- durations_data(J,D), D > 0, T = 0..D-1, not ge_s(J,T+1).
runs(J,T) :- durations_data(J,D), D > 0, horizon(H), longest(M), T = D..H+M, ge_s(J,T-D+1), not ge_s(J,T+1).

% Resource capacity: at every time, the jobs running together use at most the capacity of each resource.
:- resource(R), resource_capacities_data(R,C), horizon(H), longest(M), T = 0..H+M,
   #sum { Q,J : runs(J,T), resource_needs_data(J,R,Q) } > C.

% Makespan: the latest start time over all jobs, which is to be minimised. ge_s is monotone,
% so counting the times T at which some job starts at T or later gives that latest start time.
#minimize { 1,T : ge_s(J,T) }.

#show start_time/2.
