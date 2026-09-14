% Solving side of the swipl_clpfd integration. Runs inside the image only.
%
% `run.py` starts this driver, which consults the submission at /input/model.pl,
% reads /input/request.json, and writes the runner protocol as JSON lines on
% standard output. The submission states the model; this driver owns labelling,
% optimisation, enumeration and printing, so a submission never searches or
% prints by itself.
%
% A submission defines model/3 for satisfaction, or model/4 whose fourth
% argument is min(Expr), max(Expr) or none:
%
%     model(Instance, Vars, Outputs)
%     model(Instance, Vars, Outputs, Objective)
%
% Instance is the instance JSON as a dict, Vars the finite-domain variables to
% label, and Outputs a list of Name-Value pairs, one per declared output. A
% submission may also define labeling_options/1 to choose clpfd labelling
% options; the default is [ff].

:- use_module(library(clpfd)).
:- use_module(library(http/json)).
:- use_module(library(time)).
:- use_module(library(apply)).
:- use_module(library(error)).
:- use_module(library(lists)).

main :-
    catch(run, Error, report(Error)),
    halt.
main :-
    % run/0 failing rather than throwing is a driver bug, not a verdict about
    % the submission, but it still has to leave exactly one status behind.
    status(error, "The swipl_clpfd driver failed without reaching a verdict"),
    halt.

run :-
    read_request(Request),
    get_time(Start),
    Deadline is Start + Request.execution_timeout,
    consult('/input/model.pl'),
    search_options(Options),
    solve(Request.instance, Request.solution_limit, Options, Deadline, Status),
    get_time(End),
    Seconds is End - Start,
    status(Status, "", Seconds).

read_request(Request) :-
    setup_call_cleanup(
        open('/input/request.json', read, Stream),
        json_read_dict(Stream, Request, [value_string_as(atom)]),
        close(Stream)).

% The submission may choose clpfd labelling options, but the objective belongs
% to the driver, so min/1 and max/1 are refused here rather than honoured
% behind the driver's back.
search_options(Options) :-
    (   current_predicate(labeling_options/1),
        call(labeling_options, Given)
    ->  must_be(list, Given),
        (   member(Option, Given), functor(Option, Name, 1), memberchk(Name, [min, max])
        ->  fail_with("labeling_options/1 must not set min/1 or max/1; state the \c
                       objective through model/4 instead")
        ;   Options = Given
        )
    ;   Options = [ff]
    ).

% ---------------------------------------------------------------------------
% Solving: prove the optimum first when there is one, then enumerate distinct
% declared outputs that achieve it.

solve(Instance, Limit, Options, Deadline, Status) :-
    (   current_predicate(model/4)
    ->  bounded(Deadline, optimum(Instance, Options, Optimum), timeout(optimum))
    ;   Optimum = none
    ),
    enumerate(Instance, Limit, Options, Deadline, Optimum, Status).

% clpfd's labeling/2 enumerates in ascending order under min(Expr) and in
% descending order under max(Expr), so the first solution it reports carries the
% optimal value. Anything short of that first solution is a timeout or an
% unsatisfiable model, never a result.
optimum(Instance, Options, Optimum) :-
    build(Instance, Vars, _, Objective),
    (   Objective == none
    ->  Optimum = none
    ;   Objective =.. [_, Expression],
        (   once(labeling([Objective|Options], Vars))
        ->  Optimum is Expression
        ;   throw(verdict(unsat))
        )
    ).

enumerate(Instance, Limit, Options, Deadline, Optimum, Status) :-
    nb_setval(solution_count, 0),
    nb_setval(solutions_seen, []),
    (   bounded(Deadline, search(Instance, Limit, Options, Optimum, Found), timeout(search))
    ->  Status = Found
    ;   Status = error
    ).

search(Instance, Limit, Options, Optimum, Status) :-
    (   build(Instance, Vars, Outputs, Objective),
        fix_objective(Objective, Optimum),
        labeling(Options, Vars),
        emit_solution(Outputs),
        nb_getval(solution_count, Count),
        Count >= Limit
    ->  Status = limit
    ;   nb_getval(solution_count, Count),
        % Backtracking ran out: the model is exhausted, or it had no solution.
        (   Count > 0 -> Status = complete ; Status = unsat )
    ).

fix_objective(_, none) :- !.
fix_objective(Objective, Optimum) :-
    Objective =.. [_, Expression],
    Expression #= Optimum.

% Call the submission and label every variable it declared plus every variable
% still free in its outputs, so an output variable that no constraint mentions
% gets a value instead of reaching the protocol unbound.
build(Instance, AllVars, Outputs, Objective) :-
    (   current_predicate(model/4)
    ->  call(model, Instance, Vars, Outputs, Given),
        check_objective(Given),
        Objective = Given
    ;   current_predicate(model/3)
    ->  call(model, Instance, Vars, Outputs),
        Objective = none
    ;   fail_with("The submission defines neither model/3 nor model/4")
    ),
    check_outputs(Outputs),
    term_variables(Vars-Outputs, AllVars).

check_objective(none) :- !.
check_objective(min(_)) :- !.
check_objective(max(_)) :- !.
check_objective(Other) :-
    fail_with("The objective must be min(Expr), max(Expr) or none, not ~w", [Other]).

check_outputs(Outputs) :-
    (   is_list(Outputs), Outputs \== []
    ->  forall(member(Pair, Outputs), check_output(Pair))
    ;   fail_with("Outputs must be a nonempty list of Name-Value pairs, not ~w", [Outputs])
    ).

check_output(Name-_) :- atom(Name), !.
check_output(Other) :-
    fail_with("Each output must be Name-Value with an atom name, not ~w", [Other]).

% ---------------------------------------------------------------------------
% Output

emit_solution(Outputs) :-
    values_dict(Outputs, Dict),
    with_output_to(string(Text), json_write_dict(current_output, Dict, [width(0)])),
    nb_getval(solutions_seen, Seen),
    % Distinctness is measured over the declared outputs only.
    (   memberchk(Text, Seen)
    ->  true
    ;   nb_setval(solutions_seen, [Text|Seen]),
        record(_{type: solution, values: Dict}),
        nb_getval(solution_count, Count),
        Next is Count + 1,
        nb_setval(solution_count, Next)
    ).

values_dict(Outputs, Dict) :-
    maplist(output_pair, Outputs, Pairs),
    dict_pairs(Dict, _, Pairs).

output_pair(Name-Value, Name-Value) :-
    (   ground(Value)
    ->  true
    ;   fail_with("Declared output ~w was left unbound by labelling", [Name])
    ).

status(Status, Detail) :-
    record(_{type: status, status: Status, detail: Detail}).

status(Status, Detail, Seconds) :-
    record(_{type: status, status: Status, detail: Detail, solve_seconds: Seconds}).

record(Dict) :-
    json_write_dict(current_output, Dict, [width(0)]),
    nl(current_output),
    flush_output(current_output).

% ---------------------------------------------------------------------------
% Budget and failure reporting. Every outcome leaves exactly one status record.

bounded(Deadline, Goal, timeout(Where)) :-
    get_time(Now),
    Left is max(0.001, Deadline - Now),
    catch(call_with_time_limit(Left, Goal), time_limit_exceeded, throw(verdict(timeout(Where)))).

fail_with(Format) :- fail_with(Format, []).

fail_with(Format, Arguments) :-
    format(atom(Message), Format, Arguments),
    throw(submission_error(Message)).

report(verdict(unsat)) :- !,
    status(unsat, "").
report(verdict(timeout(Where))) :- !,
    format(atom(Detail), "The execution budget ran out during ~w", [Where]),
    status(timeout, Detail).
report(submission_error(Message)) :- !,
    status(error, Message).
report(Error) :-
    print_message(error, Error),
    format(atom(Message), "~w", [Error]),
    status(error, Message).
