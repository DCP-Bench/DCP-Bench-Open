% Schedule four tasks on two machines, respecting precedences, to minimise the
% makespan.
% Shows: start variables, each end given by a constraint, cumulative/2 with
% task/5 and a resource limit, precedences as inequalities, and minimise.
:- use_module(library(clpfd)).
:- initialization(main, main).

% task(Name, Duration), and precedence(Before, After).
task(t1, 3).
task(t2, 2).
task(t3, 2).
task(t4, 4).
precedence(t1, t3).
precedence(t2, t4).

main :-
    findall(Name-Duration, task(Name, Duration), Tasks),
    findall(Before-After, precedence(Before, After), Precedences),
    pairs_keys(Tasks, Names),
    length(Tasks, N),
    length(Starts, N),
    length(Ends, N),
    Starts ins 0..20,
    Ends ins 0..20,
    % Built with maplist, not findall: findall/3 would post the constraints on copies.
    maplist(as_task, Tasks, Starts, Ends, Resource),
    cumulative(Resource, [limit(2)]),
    maplist(precedence_constraint(Names, Starts, Ends), Precedences),
    Makespan in 0..20,
    maplist(ends_by(Makespan), Ends),
    once(labeling([min(Makespan)], [Makespan|Starts])),
    format("Starts: ~w~n", [Starts]),
    format("Makespan: ~w~n", [Makespan]).

% One task of the resource: it runs from Start for Duration and ends at End.
as_task(Name-Duration, Start, End, task(Start, Duration, End, 1, Name)) :-
    End #= Start + Duration.

% The task Before must end before the task After starts.
precedence_constraint(Names, Starts, Ends, Before-After) :-
    nth1(I, Names, Before),
    nth1(J, Names, After),
    nth1(I, Ends, EndBefore),
    nth1(J, Starts, StartAfter),
    StartAfter #>= EndBefore.

ends_by(Makespan, End) :-
    End #=< Makespan.
