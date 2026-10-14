:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(pairs)).

% Resource-constrained project scheduling: start every job so that the
% precedence relations hold and, at every moment, the jobs running together use
% no more of each renewable resource than its capacity, minimising the makespan,
% which the problem defines as the latest start time of any job.

% Search: always fix next the job that can start earliest, at its earliest
% start (the "set times" rule of scheduling); on backtracking the job is
% postponed and another earliest-startable job is tried.
labeling_options([min, up, step]).

model(Instance, Vars, [start_time-Starts], min(Makespan)) :-
    Durations = Instance.durations_data,          % Durations[job]
    Needs = Instance.resource_needs_data,         % Needs[job][resource]
    Capacities = Instance.resource_capacities_data,
    Links = Instance.successors_link_data,        % [A, B]: job B starts after job A has finished, jobs counted from 0
    length(Durations, NJobs),
    Last is NJobs - 1,
    numlist(0, Last, Jobs),
    maplist(predecessors(Links), Jobs, Preds),

    % Horizon. The reference bounds every start by the sum of the durations.
    % A schedule built greedily from the instance (serial schedule generation:
    % take the jobs in a precedence-respecting priority order and start each at
    % the earliest time its predecessors and the free capacity allow) is
    % feasible, so the optimal makespan is at most its latest start, and no
    % optimal schedule starts a job later than that. The smaller of the two
    % bounds is the domain, so the time-indexed resource constraints below are
    % posted over far fewer time points.
    sum_list(Durations, SumDurations),
    maplist(successors(Links), Jobs, Succs),
    tails(Durations, Succs, Tails),
    findall(M, ( member(Rule, [tail, index]),
                 greedy_makespan(Rule, Jobs, Durations, Needs, Capacities,
                                 Preds, Tails, SumDurations, M) ),
            Greedy),
    min_list([SumDurations|Greedy], Horizon),

    % Starts[j] = when job j starts
    length(Starts, NJobs),
    Starts ins 0..Horizon,

    % a job can only start when its predecessor has finished
    maplist(precedence(Starts, Durations), Links),

    % at any time the jobs in progress need no more of a resource than is available
    transpose(Needs, NeedsPerResource),
    maplist(resource(Starts, Durations), NeedsPerResource, Capacities),

    % Implied: two jobs whose needs of some resource together exceed its
    % capacity can never run at the same time, so one finishes before the other
    % starts. cumulative/2 only sees this once one of the two is fixed in time.
    findall(I-J, incompatible(Jobs, Durations, Needs, Capacities, I, J), Pairs),
    maplist(not_overlapping(Starts, Durations), Pairs),

    % the makespan is the latest start of any job; it is minimised, so stating
    % it as at least every start is enough
    Makespan in 0..Horizon,
    maplist(at_most(Makespan), Starts),
    append(Starts, [Makespan], Vars).

predecessors(Links, J, Ps) :- findall(A, member([A, J], Links), Ps).
successors(Links, J, Ss) :- findall(B, member([J, B], Links), Ss).

precedence(Starts, Durations, [A, B]) :-
    nth0(A, Starts, StartA),
    nth0(B, Starts, StartB),
    nth0(A, Durations, DurationA),
    StartB #>= StartA + DurationA.

at_most(Makespan, Start) :- Makespan #>= Start.

% cumulative/2 over task(Start, Duration, End, Demand, Id). A job of length 0
% uses no resource at any moment, and cumulative/2 rejects a task of length 0,
% so such a job is left out.
resource(Starts, Durations, Demands, Capacity) :-
    tasks(Starts, Durations, Demands, 1, Tasks),
    cumulative(Tasks, [limit(Capacity)]).

tasks([], [], [], _, []).
tasks([Start|Starts], [Duration|Durations], [Demand|Demands], Id, Tasks) :-
    Next is Id + 1,
    (   Duration =:= 0
    ->  Tasks = Rest
    ;   End #= Start + Duration,
        Tasks = [task(Start, Duration, End, Demand, Id)|Rest]
    ),
    tasks(Starts, Durations, Demands, Next, Rest).

incompatible(Jobs, Durations, Needs, Capacities, I, J) :-
    member(I, Jobs), member(J, Jobs), I < J,
    nth0(I, Durations, DI), DI > 0,
    nth0(J, Durations, DJ), DJ > 0,
    nth0(I, Needs, NI), nth0(J, Needs, NJ),
    once(( nth1(K, Capacities, Cap), nth1(K, NI, RI), nth1(K, NJ, RJ),
           RI + RJ > Cap )).

not_overlapping(Starts, Durations, I-J) :-
    nth0(I, Starts, SI), nth0(J, Starts, SJ),
    nth0(I, Durations, DI), nth0(J, Durations, DJ),
    SI + DI #=< SJ #\/ SJ + DJ #=< SI.

% ---------------------------------------------------------------------------
% Ground computations on the instance data, used only for the horizon.

% Tails[j] = Durations[j] + the longest chain of durations after job j along
% the successor relation (a longest-path fixpoint over the precedence graph).
tails(Durations, Succs, Tails) :-
    length(Durations, N),
    tails_iterate(N, Durations, Succs, Durations, Tails).

tails_iterate(0, _, _, Tails, Tails) :- !.
tails_iterate(K, Durations, Succs, Current, Tails) :-
    maplist(tail_step(Current), Durations, Succs, Next),
    K1 is K - 1,
    tails_iterate(K1, Durations, Succs, Next, Tails).

tail_step(Current, Duration, Ss, Tail) :-
    findall(T, (member(S, Ss), nth0(S, Current, T)), Ts),
    max_list([0|Ts], Longest),
    Tail is Duration + Longest.

% Serial schedule generation. Rule `tail` takes, among the jobs whose
% predecessors are all scheduled, the one with the longest tail first (the
% latest-start-time rule); rule `index` takes the lowest job number. Fails if
% some job can never fit, in which case only the reference bound is used.
greedy_makespan(Rule, Jobs, Durations, Needs, Capacities, Preds, Tails, Limit, Makespan) :-
    sgs(Jobs, Rule, Durations, Needs, Capacities, Preds, Tails, Limit, [], Placed),
    pairs_values(Placed, Placements),
    findall(S, member(placed(S, _, _), Placements), Ss),
    max_list(Ss, Makespan).

sgs([], _, _, _, _, _, _, _, Placed, Placed) :- !.
sgs(Unscheduled, Rule, Durations, Needs, Capacities, Preds, Tails, Limit, Placed0, Placed) :-
    findall(Key-J,
            ( member(J, Unscheduled),
              nth0(J, Preds, Ps),
              forall(member(P, Ps), memberchk(P-_, Placed0)),
              priority(Rule, J, Tails, Key) ),
            Eligible),
    keysort(Eligible, [_-J|_]),
    nth0(J, Durations, D),
    nth0(J, Needs, Need),
    nth0(J, Preds, Ps),
    findall(E, ( member(P, Ps), memberchk(P-placed(SP, DP, _), Placed0), E is SP + DP ), Es),
    max_list([0|Es], Earliest),
    between(Earliest, Limit, T),
    fits(T, D, Need, Capacities, Placed0),
    !,
    selectchk(J, Unscheduled, Rest),
    sgs(Rest, Rule, Durations, Needs, Capacities, Preds, Tails, Limit,
        [J-placed(T, D, Need)|Placed0], Placed).

priority(tail, J, Tails, NegTail-J) :- nth0(J, Tails, T), NegTail is -T.
priority(index, J, _, J).

% Job of length D needing Need fits from time T when, at every moment it runs,
% the jobs already placed leave enough of every resource.
fits(T, D, Need, Capacities, Placed) :-
    End is T + D - 1,
    forall(between(T, End, Time),
           ( findall(N, ( member(_-placed(S, DS, N), Placed), S =< Time, Time < S + DS ), Running),
             usage_ok(Running, Need, Capacities) )).

usage_ok(Running, Need, Capacities) :-
    foldl(add_needs, Running, Need, Total),
    maplist(=<, Total, Capacities).

add_needs(N, Acc0, Acc) :- maplist(plus, N, Acc0, Acc).
