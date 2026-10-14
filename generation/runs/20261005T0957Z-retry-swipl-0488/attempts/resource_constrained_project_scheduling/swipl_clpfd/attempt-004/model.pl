:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(pairs)).
:- use_module(library(ordsets)).

% Resource-constrained project scheduling: start every job so that the
% precedence relations hold and, at every moment, the jobs running together use
% no more of each renewable resource than its capacity, minimising the makespan,
% which the problem defines as the latest start time of any job.

% Search: the makespan first, smallest value first (its domain, between the
% bounds below and the greedy horizon, is the smallest one), so every job's
% latest start is known while jobs are placed; then the job with the fewest
% possible start times, at its earliest start.
labeling_options([ff, up, step]).

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

    % Implied (one-machine bound): jobs that pairwise cannot overlap, because
    % one precedes the other or because together they exceed a capacity, run
    % one after another. For such a set whose jobs all have a successor (so
    % each finishes no later than some job starts), the last of them finishes
    % at least the sum of their durations after the first one starts, and the
    % chain of successors after it still has to start; hence
    %   makespan >= earliest start in the set + sum of durations
    %               + shortest successor chain after a job of the set.
    % The sets are built greedily from the instance (one per job, adding jobs
    % longest first), then restricted to the jobs whose earliest possible start
    % is at least some threshold, and to those whose successor chain is at
    % least some threshold, because a set with a late first job or long chains
    % gives a larger bound than the whole set.
    maplist(reachable_after(Succs, NJobs), Jobs, Reach),
    heads(Durations, Preds, Heads),
    after_chains(Durations, Succs, Chains),
    exclusive_sets(Jobs, Durations, Needs, Capacities, Succs, Reach, Heads, Chains, Sets),
    maplist(one_machine_bound(Makespan, Starts, Durations, Chains), Sets),
    Vars = [Makespan|Starts].

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

one_machine_bound(Makespan, Starts, Durations, Chains, Set) :-
    % the starts are gathered by mapping, not findall/3, which would copy them
    maplist(start_of(Starts), Set, Ss),
    findall(D, (member(J, Set), nth0(J, Durations, D)), Ds),
    findall(C, (member(J, Set), nth0(J, Chains, C)), Cs),
    sum_list(Ds, Work),
    min_list(Cs, Chain),
    min_expression(Ss, FirstStart),
    Makespan #>= FirstStart + Work + Chain.

start_of(Starts, J, S) :- nth0(J, Starts, S).

min_expression([T], T) :- !.
min_expression([T|Ts], min(T, E)) :- min_expression(Ts, E).

% ---------------------------------------------------------------------------
% Ground computations on the instance data, used for the horizon and for the
% sets of jobs that cannot overlap.

% Reach = every job that follows J through one or more precedence links
reachable_after(Succs, N, J, Reach) :-
    reach_iterate(N, Succs, [J], [], Reach).

reach_iterate(_, _, [], Reach, Reach) :- !.
reach_iterate(K, Succs, Frontier, Seen, Reach) :-
    findall(S, (member(F, Frontier), nth0(F, Succs, Ss), member(S, Ss)), New0),
    sort(New0, New1),
    ord_subtract(New1, Seen, New),
    ord_union(Seen, New, Seen1),
    reach_iterate(K, Succs, New, Seen1, Reach).

% Heads[j] = earliest start of job j along the predecessor chains
heads(Durations, Preds, Heads) :-
    length(Durations, N),
    length(Zeros, N), maplist(=(0), Zeros),
    heads_iterate(N, Durations, Preds, Zeros, Heads).

heads_iterate(0, _, _, Heads, Heads) :- !.
heads_iterate(K, Durations, Preds, Current, Heads) :-
    maplist(head_step(Durations, Current), Preds, Next),
    K1 is K - 1,
    heads_iterate(K1, Durations, Preds, Next, Heads).

head_step(Durations, Current, Ps, Head) :-
    findall(E, (member(P, Ps), nth0(P, Current, H), nth0(P, Durations, D), E is H + D), Es),
    max_list([0|Es], Head).

% Chains[j] = how long after job j ends some job must still start: the longest
% path over successors, where a successor counts its own duration only when it
% has a successor itself (otherwise only its start must lie within the makespan)
after_chains(Durations, Succs, Chains) :-
    length(Durations, N),
    length(Zeros, N), maplist(=(0), Zeros),
    chains_iterate(N, Durations, Succs, Zeros, Chains).

chains_iterate(0, _, _, Chains, Chains) :- !.
chains_iterate(K, Durations, Succs, Current, Chains) :-
    maplist(chain_step(Durations, Succs, Current), Succs, Next),
    K1 is K - 1,
    chains_iterate(K1, Durations, Succs, Next, Chains).

chain_step(Durations, Succs, Current, Ss, Chain) :-
    findall(L, ( member(S, Ss), nth0(S, Succs, SSs),
                 (   SSs == [] -> L = 0
                 ;   nth0(S, Durations, D), nth0(S, Current, C), L is D + C
                 ) ), Ls),
    max_list([0|Ls], Chain).

% Jobs I and J cannot overlap: both take time and one precedes the other, or
% together they need more of some resource than its capacity
exclusive(Durations, Needs, Capacities, Reach, I, J) :-
    I =\= J,
    nth0(I, Durations, DI), DI > 0,
    nth0(J, Durations, DJ), DJ > 0,
    (   nth0(I, Reach, RI), ord_memberchk(J, RI) -> true
    ;   nth0(J, Reach, RJ), ord_memberchk(I, RJ) -> true
    ;   nth0(I, Needs, NI), nth0(J, Needs, NJ),
        once(( nth1(K, Capacities, Cap), nth1(K, NI, A), nth1(K, NJ, B), A + B > Cap ))
    ).

exclusive_sets(Jobs, Durations, Needs, Capacities, Succs, Reach, Heads, Chains, Sets) :-
    findall(J, ( member(J, Jobs), nth0(J, Durations, D), D > 0,
                 nth0(J, Succs, Ss), Ss \== [] ), Candidates),
    findall(NegD-J, ( member(J, Candidates), nth0(J, Durations, D), NegD is -D ), Keyed),
    keysort(Keyed, ByLength0),
    pairs_values(ByLength0, ByLength),
    findall(Set, ( member(Seed, Candidates),
                   foldl(grow_set(Durations, Needs, Capacities, Reach), ByLength, [Seed], Set0),
                   sort(Set0, Set) ), Seeds0),
    sort(Seeds0, Seeds),
    findall(Sub, ( member(Set, Seeds),
                   (   member(J, Set), nth0(J, Heads, H),
                       include(at_least(Heads, H), Set, Sub)
                   ;   member(J, Set), nth0(J, Chains, C),
                       include(at_least(Chains, C), Set, Sub)
                   ) ), Subs0),
    sort(Subs0, Sets).

grow_set(Durations, Needs, Capacities, Reach, J, Set0, Set) :-
    (   \+ memberchk(J, Set0),
        forall(member(I, Set0), exclusive(Durations, Needs, Capacities, Reach, I, J))
    ->  Set = [J|Set0]
    ;   Set = Set0
    ).

at_least(Values, Threshold, J) :- nth0(J, Values, V), V >= Threshold.

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
