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
    % Load[m] is the work all jobs bring to machine m, and MinTail[m] the least
    % work any job still has after machine m. Both are constants of the
    % instance used only in the implied bound below.
    maplist(sum_list, TimeOn, Loads),
    maplist(tails, ProcessTime, TailRows),
    transpose(TailRows, TailColumns),
    maplist(min_list, TailColumns, MinTails),

    % Each job runs on a machine as soon as the machine is free and the job
    % has left the previous machine. Delaying a job never lowers the makespan,
    % so fixing starts to the earliest possible time keeps the same optimum
    % and makes every time follow from the sequence alone.
    length(NoEnds, NMachines),
    maplist(=(0), NoEnds),
    schedule(Sequence, TimeOn, NoEnds, Loads, MinTails, Horizon, Makespan, LastEnds),

    % The makespan is the completion time of the last job on the last machine
    % (completion times never decrease along the sequence or the machines, so
    % it is also the largest completion time of all).
    last(LastEnds, Makespan),

    % Implied bound: a machine handles every job one after the other, so the
    % makespan is at least the total work assigned to that machine.
    maplist({Makespan}/[Load]>>(Makespan #>= Load), Loads).

% Search in the order of the sequence: choose who goes first, then second, ...
% so the bounds below see a growing prefix of fixed jobs.
labeling_options([leftmost]).

% tails(+Row, -Tails): Tails[m] is the work a job still has after machine m.
tails([], []).
tails([_|Rest], [Tail|Tails]) :-
    sum_list(Rest, Tail),
    tails(Rest, Tails).

% schedule(+Sequence, +TimeOn, +EndsAbove, +RemsAbove, +MinTails, +Horizon,
%          +Makespan, -LastEnds): place the jobs of the sequence one after the
% other. EndsAbove holds, per machine, the completion time of the job processed
% just before, and RemsAbove the work on that machine still to be done by the
% jobs not yet placed.
schedule([], _, Ends, _, _, _, _, Ends).
schedule([Job|Jobs], TimeOn, EndsAbove, RemsAbove, MinTails, Horizon, Makespan, LastEnds) :-
    place(Job, TimeOn, EndsAbove, RemsAbove, MinTails, 0, Horizon, Makespan, Ends, Rems),
    schedule(Jobs, TimeOn, Ends, Rems, MinTails, Horizon, Makespan, LastEnds).

% place(+Job, +TimeOn, +EndsAbove, +RemsAbove, +MinTails, +EndLeft, +Horizon,
%       +Makespan, -Ends, -Rems): run the job on every machine in order. It
% starts on a machine when it has finished on the machine before (EndLeft) and
% the previous job of the sequence has finished on this machine (EndAbove).
place(_, [], [], [], [], _, _, _, [], []).
place(Job, [Times|TimeOns], [EndAbove|EndsAbove], [RemAbove|RemsAbove], [MinTail|MinTails],
      EndLeft, Horizon, Makespan, [End|Ends], [Rem|Rems]) :-
    element(Job, Times, Duration),
    End in 0..Horizon,
    End #= max(EndLeft, EndAbove) + Duration,
    % work still waiting for this machine once this job is placed
    Rem #= RemAbove - Duration,
    % Implied bound: the jobs still to come need Rem more time on this machine
    % after End, and the last of them then still has to cross the machines
    % behind it, which takes at least MinTail.
    Makespan #>= End + Rem + MinTail,
    place(Job, TimeOns, EndsAbove, RemsAbove, MinTails, End, Horizon, Makespan, Ends, Rems).
