% Job shop: several jobs, each a sequence of tasks, each task on a given machine.
% Minimise the makespan, the time at which all jobs are completed.
:- lib(ic).
:- lib(ic_edge_finder).

% Instance: jobs_data = list of jobs, each a list of [Machine, Duration] tasks (0-based machines).
model(Instance, Starts, [makespan-Makespan], min(Makespan)) :-
    memberchk(jobs_data-Jobs, Instance),
    total_duration(Jobs, 0, H),
    % One start variable per task. Its domain is bounded by the sum of all durations.
    ( foreach(Job, Jobs), foreach(Ts, JobTasks), param(H) do
        make_tasks(Job, H, Ts)
    ),
    % No task for a job can be started until the previous task for that job is completed.
    ( foreach(Ts, JobTasks) do
        chain(Ts)
    ),
    flatten(JobTasks, AllTasks),
    % The makespan is the time at which all jobs are completed.
    % A task, once started, must run to completion: it ends at its start plus its duration.
    Makespan :: 0..H,
    ( foreach(t(_,S,D), AllTasks), param(Makespan) do
        S + D #=< Makespan
    ),
    % A machine can only work on one task at a time.
    ( foreach(t(M,_,_), AllTasks), fromto(-1, A, B, MaxM) do
        B is max(A, M)
    ),
    ( for(M, 0, MaxM), param(AllTasks) do
        machine_no_overlap(M, AllTasks)
    ),
    ( foreach(t(_,S,_), AllTasks), foreach(S, Starts) do
        true
    ).

% Labelling: smallest earliest start first, which suits scheduling start times.
search_goal(Starts) :-
    search(Starts, 0, smallest, indomain_min, complete, []).

total_duration([], H, H).
total_duration([Job|Jobs], H0, H) :-
    job_duration(Job, H0, H1),
    total_duration(Jobs, H1, H).

job_duration([], H, H).
job_duration([[_,D]|Tasks], H0, H) :-
    H1 is H0 + D,
    job_duration(Tasks, H1, H).

make_tasks([], _, []).
make_tasks([[M,D]|Rest], H, [t(M,S,D)|Ts]) :-
    S :: 0..H,
    make_tasks(Rest, H, Ts).

chain([]).
chain([_]).
chain([t(_,S1,D1), T2|Rest]) :-
    T2 = t(_,S2,_),
    S1 + D1 #=< S2,
    chain([T2|Rest]).

% Start and duration lists of the tasks that use machine M.
% Plain recursion, not findall/3: findall would copy the variables.
on_machine(_, [], [], []).
on_machine(M, [t(M1,S,D)|Ts], Ss, Ds) :-
    ( M1 == M -> Ss = [S|Ss1], Ds = [D|Ds1] ; Ss = Ss1, Ds = Ds1 ),
    on_machine(M, Ts, Ss1, Ds1).

machine_no_overlap(M, AllTasks) :-
    on_machine(M, AllTasks, Ss, Ds),
    ( Ss == [] -> true ; disjunctive(Ss, Ds) ).
