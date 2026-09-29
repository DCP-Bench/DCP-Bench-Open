:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Resource-constrained project scheduling: start every job so that the
% precedence relations hold and, at every moment, the jobs running together use
% no more of each renewable resource than its capacity, finishing the project
% as early as possible.
model(Instance, [Makespan|Starts], [start_time-Starts], min(Makespan)) :-
    Durations = Instance.durations_data,
    Needs = Instance.resource_needs_data,           % Needs[job][resource]
    Capacities = Instance.resource_capacities_data,
    Precedences = Instance.successors_link_data,    % [A, B]: job B starts after job A has finished, jobs counted from 0
    length(Durations, NJobs),
    sum_list(Durations, Horizon),   % a schedule that runs one job at a time is never longer

    % Starts[j] = when job j starts
    length(Starts, NJobs),
    Starts ins 0..Horizon,

    % a job can only start when its predecessor has finished
    maplist({Starts, Durations}/[[A, B]]>>(nth0(A, Starts, StartA), nth0(B, Starts, StartB), nth0(A, Durations, DurationA),
                                          StartB #>= StartA + DurationA), Precedences),

    % at any time the jobs in progress need no more of a resource than is available
    transpose(Needs, NeedsPerResource),
    maplist({Starts, Durations}/[Demand, Capacity]>>(
                tasks(Starts, Durations, Demand, 1, Tasks),
                cumulative(Tasks, [limit(Capacity)])),
            NeedsPerResource, Capacities),

    % the project ends with its latest starting job (the last job is a zero-length
    % dummy): the makespan is at least every start and is minimised
    Makespan in 0..Horizon,
    maplist({Makespan}/[Start]>>(Makespan #>= Start), Starts).

% tasks(+Starts, +Durations, +Demands, +Id, -Tasks): each job as task(Start, Duration, End, Demand, Id)
tasks([], [], [], _, []).
tasks([Start|Starts], [Duration|Durations], [Demand|Demands], Id, [task(Start, Duration, End, Demand, Id)|Tasks]) :-
    End #= Start + Duration,
    Next is Id + 1,
    tasks(Starts, Durations, Demands, Next, Tasks).
