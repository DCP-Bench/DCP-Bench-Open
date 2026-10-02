:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% Job shop: every job is a sequence of tasks, each to be run on a given machine
% for a given time. A task starts only after the previous task of its job has
% finished, and a machine runs one task at a time. Minimise the makespan, the
% time when the last task finishes.
model(Instance, Orders, [makespan-Makespan], min(Makespan)) :-
    JobsData = Instance.jobs_data,          % JobsData[j][k] = [machine, duration]

    % No schedule needs to run longer than all the tasks one after the other;
    % this is the upper bound on every time variable.
    findall(Duration, (member(Job, JobsData), member([_, Duration], Job)), Durations),
    sum_list(Durations, Horizon),
    Makespan in 0..Horizon,

    % task(Machine, Start, Duration) for every task of every job.
    maplist({Horizon}/[Job, Tasks]>>job_tasks(Job, Horizon, Tasks), JobsData, JobTasks),

    % a task starts after the previous task of its job is completed, and the
    % makespan comes after the last task of each job
    maplist({Makespan}/[Tasks]>>in_sequence(Tasks, Makespan), JobTasks),

    % a machine can only work on one task at a time
    findall(Machine, (member(Job, JobsData), member([Machine, _], Job)), Used),
    sort(Used, Machines),
    append(JobTasks, AllTasks),
    maplist({AllTasks, Makespan}/[Machine, Order]>>
                (include(on_machine(Machine), AllTasks, OnMachine),
                 one_at_a_time(OnMachine, Makespan, Order)),
            Machines, MachineOrders),
    append(MachineOrders, Orders).

% job_tasks(+Job, +Horizon, -Tasks): one task term per [Machine, Duration] pair.
job_tasks([], _, []).
job_tasks([[Machine, Duration]|Rest], Horizon, [task(Machine, Start, Duration)|Tasks]) :-
    Start in 0..Horizon,
    job_tasks(Rest, Horizon, Tasks).

% in_sequence(+Tasks, +Makespan): the tasks of one job run in the given order,
% and the last one finishes by the makespan.
in_sequence([], _).
in_sequence([task(_, Start, Duration)], Makespan) :- !,
    Start + Duration #=< Makespan.
in_sequence([task(_, Start, Duration), Next|Rest], Makespan) :-
    Next = task(_, NextStart, _),
    Start + Duration #=< NextStart,
    in_sequence([Next|Rest], Makespan).

on_machine(Machine, task(Machine, _, _)).

% one_at_a_time(+Tasks, +Makespan, -Order): the tasks share a machine. For every
% two of them one runs before the other; Order lists a 0/1 variable per pair
% telling which, and these are the variables the search decides. The start
% times are not decided directly: once every pair is ordered the constraints
% left on them are differences between start times, so propagation either
% fails or leaves a schedule. Deciding the order instead of the start times
% also keeps the search from counting one schedule once per way of delaying
% a task.
one_at_a_time(Tasks, Makespan, Order) :-
    % the machine needs the sum of its tasks' durations in any schedule
    findall(Duration, member(task(_, _, Duration), Tasks), Durations),
    sum_list(Durations, Load),
    Makespan #>= Load,
    pairwise_order(Tasks, Order).

pairwise_order([], []).
pairwise_order([Task|Tasks], Order) :-
    maplist(first_or_second(Task), Tasks, Here),
    pairwise_order(Tasks, There),
    append(Here, There, Order).

% first_or_second(+Task1, +Task2, -Before): Before is 1 when Task1 finishes
% before Task2 starts and 0 when Task2 finishes before Task1 starts.
first_or_second(task(_, Start1, Duration1), task(_, Start2, Duration2), Before) :-
    Before in 0..1,
    Before #= 1 #==> Start1 + Duration1 #=< Start2,
    Before #= 0 #==> Start2 + Duration2 #=< Start1.
