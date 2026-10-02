:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% Flow shop scheduling: every job visits the machines in the same order. Find
% the order of the jobs that minimises the makespan, the time when the last job
% leaves the last machine.
model(Instance, Sequence, [makespan-Makespan], min(Makespan)) :-
    Jobs = Instance.jobs,
    Machines = Instance.machines,
    ProcessTime = Instance.process_time,    % ProcessTime[job][machine]
    length(Jobs, NJobs),
    length(Machines, NMachines),

    % No schedule needs to run longer than all the work done one task after
    % the other; this is the upper bound on every time variable.
    append(ProcessTime, AllTimes),
    sum_list(AllTimes, Horizon),

    % Sequence[k] is the job processed k-th (1-based, to index with element/3).
    length(Sequence, NJobs),
    Sequence ins 1..NJobs,
    % every job appears exactly once in the sequence
    all_distinct(Sequence),

    % TimeOn[m] lists the processing time of every job on machine m.
    transpose(ProcessTime, TimeOn),

    % Each job runs on a machine as soon as the machine is free and the job
    % has left the previous machine. Delaying a job never lowers the makespan,
    % so fixing starts to the earliest possible time keeps the same optimum
    % and makes every time follow from the sequence alone.
    length(NoEnds, NMachines),
    maplist(=(0), NoEnds),
    schedule(Sequence, TimeOn, NoEnds, Horizon, LastEnds),

    % The makespan is the completion time of the last job on the last machine
    % (completion times never decrease along the sequence or the machines, so
    % it is also the largest completion time of all).
    last(LastEnds, Makespan),

    % Implied bound: a machine handles every job one after the other, so the
    % makespan is at least the total work assigned to that machine.
    maplist({Makespan}/[Times]>>(sum_list(Times, Load), Makespan #>= Load), TimeOn).

% schedule(+Sequence, +TimeOn, +EndsAbove, +Horizon, -LastEnds): place the jobs
% of the sequence one after the other; EndsAbove holds, per machine, the
% completion time of the job processed just before.
schedule([], _, Ends, _, Ends).
schedule([Job|Jobs], TimeOn, EndsAbove, Horizon, LastEnds) :-
    place(Job, TimeOn, EndsAbove, 0, Horizon, Ends),
    schedule(Jobs, TimeOn, Ends, Horizon, LastEnds).

% place(+Job, +TimeOn, +EndsAbove, +EndLeft, +Horizon, -Ends): run the job on
% every machine in order. It starts on a machine when it has finished on the
% machine before (EndLeft) and the previous job of the sequence has finished on
% this machine (EndAbove).
place(_, [], [], _, _, []).
place(Job, [Times|TimeOns], [EndAbove|EndsAbove], EndLeft, Horizon, [End|Ends]) :-
    element(Job, Times, Duration),
    End in 0..Horizon,
    End #= max(EndLeft, EndAbove) + Duration,
    place(Job, TimeOns, EndsAbove, End, Horizon, Ends).
