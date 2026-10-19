% Solving side of the eclipse_clp integration. Runs inside the image only.
%
% `run.py` starts this driver with `eclipse.exe -f driver.ecl -e dcp_main`. The driver
% and the submission share module `user`, so every driver predicate is prefixed `dcp_`.
% The driver reads the request term from /tmp/dcp_request.ecl, compiles the
% submission /input/model.ecl into module `user`, and writes the runner protocol
% as JSON lines to /tmp/dcp_protocol.jsonl. Standard output is never part of the
% protocol, so a submission that prints cannot corrupt it. ECLiPSe's own error and
% warning messages go to /tmp/dcp_messages.txt, which the driver quotes in an
% `error` status and `run.py` forwards to stderr.
%
% A submission defines model/3 for satisfaction, or model/4 whose fourth argument
% is min(Expr), max(Expr) or none:
%
%     model(Instance, Vars, Outputs)
%     model(Instance, Vars, Outputs, Objective)
%
% Instance is a list of Key-Value pairs, Vars the variables to label, Outputs a
% nonempty list of Name-Value pairs. A submission may also define search_goal/1 to
% choose how Vars are labelled; the default is labeling(Vars).
%
% The driver owns the objective: it posts Cost #= Expr in the submission's own
% module `user`, so ic, gfd or fd constraints are used as the submission loaded
% them.

:- lib(branch_and_bound).
:- lib(timeout).

:- local variable(dcp_count), variable(dcp_seen).

dcp_main :-
    catch(dcp_run, Ball, dcp_report(Ball)),
    close_all,
    halt.
dcp_main :-
    % run/0 failing rather than throwing is a driver bug, not a verdict about the
    % submission, but it still has to leave exactly one status behind.
    dcp_status(error, "The eclipse_clp driver failed without reaching a verdict", none),
    close_all,
    halt.

dcp_run :-
    open('/tmp/dcp_protocol.jsonl', write, _, [alias(dcp_protocol)]),
    open('/tmp/dcp_messages.txt', write, Messages, [alias(dcp_messages)]),
    open('/dev/null', write, Null),
    set_stream(error, Messages),
    set_stream(warning_output, Messages),
    set_stream(log_output, Null),
    open('/tmp/dcp_request.ecl', read, In),
    read(In, request(Instance, Limit, Budget)),
    close(In),
    statistics(session_time, Start),
    Deadline is Start + Budget,
    load_submission,
    dcp_solve(Instance, Limit, Deadline, Status),
    statistics(session_time, End),
    Seconds is End - Start,
    dcp_status(Status, "", Seconds).

close_all :-
    catch(close(dcp_protocol), _, true),
    catch(close(dcp_messages), _, true).

load_submission :-
    call(compile('/input/model.ecl'), user),
    (   dcp_messages_text(Text), substring(Text, "syntax error", _)
    ->  dcp_fail_with(Text)
    ;   true
    ).

% ---------------------------------------------------------------------------
% Solving: prove the optimum first when there is one, then enumerate distinct
% declared outputs that achieve it.

dcp_solve(Instance, Limit, Deadline, Status) :-
    setval(dcp_count, 0),
    setval(dcp_seen, []),
    (   dcp_defined(model, 4)
    ->  dcp_bounded(Deadline, dcp_optimum(Instance, Optimum), optimum)
    ;   Optimum = none
    ),
    getval(dcp_count, Count),
    (   Optimum == unsat
    ->  Status = unsat
    ;   Count >= Limit
    ->  Status = limit
    ;   dcp_bounded(Deadline, dcp_enumerate(Instance, Limit, Optimum, Status), search)
    ).

% Branch and bound improves the incumbent by at least 1 until the search space
% is exhausted, so the solution it returns is optimal; it is reported here, after
% the proof. A model that fails, or branch and bound finding nothing, is `unsat`.
% Running out of time leaves through the timeout exception and reports nothing.
dcp_optimum(Instance, Optimum) :-
    (   dcp_build(Instance, Vars, Outputs, Objective)
    ->  (   Objective == none
        ->  Optimum = none
        ;   dcp_objective(Objective, Direction, Expression),
            dcp_post(#=(Cost, Expression)),
            (   Direction == min
            ->  Target = Cost
            ;   dcp_post(#=(Target, -(Cost)))
            ),
            (   bb_min(dcp_search_all(Vars, Outputs, Expression-Cost), Target,
                       bb_options{strategy:continue, delta:1, factor:1})
            ->  (   integer(Cost)
                ->  Optimum = Cost
                ;   dcp_fail_with("The objective is not an integer after search: %w", [Cost])
                ),
                dcp_report_solution(Outputs)
            ;   Optimum = unsat
            )
        )
    ;   Optimum = unsat
    ).

dcp_enumerate(Instance, Limit, Optimum, Status) :-
    (   dcp_build(Instance, Vars, Outputs, Objective),
        dcp_fix_objective(Objective, Optimum),
        dcp_not_reported(Outputs),
        dcp_search_all(Vars, Outputs, Objective),
        dcp_report_solution(Outputs),
        getval(dcp_count, Count),
        Count >= Limit
    ->  Status = limit
    ;   getval(dcp_count, Count),
        % Backtracking ran out: the model is exhausted, or it had no solution.
        (   Count > 0 -> Status = complete ; Status = unsat )
    ).

% Fails when the outputs are already ground and equal to a reported solution: no other
% output assignment is left, so the search below would only visit duplicates (an output
% that is just the pinned optimum, for example).
dcp_not_reported(Outputs) :-
    (   term_variables(Outputs, [])
    ->  getval(dcp_seen, Seen),
        \+ memberchk(Outputs, Seen)
    ;   true
    ).

dcp_fix_objective(none, _) :- !.
dcp_fix_objective(Objective, Optimum) :-
    dcp_objective(Objective, _, Expression),
    dcp_post(#=(Expression, Optimum)).

% Label Vars the way the submission asks (search_goal/1) or with labeling/1, then
% every variable still free in the outputs or the objective, so that an output no
% constraint mentions gets a value instead of reaching the protocol unbound.
dcp_search_all(Vars, Outputs, Extra) :-
    (   dcp_defined(search_goal, 1)
    ->  call(search_goal(Vars), user)
    ;   dcp_label(Vars)
    ),
    term_variables(Outputs-Extra, Rest),
    dcp_label(Rest).

% Nothing to label needs no solver library, so a model of plain arithmetic works.
dcp_label([]) :- !.
dcp_label(Vars) :-
    call(labeling(Vars), user).

% Call the submission and check the shape of what it returned.
dcp_build(Instance, Vars, Outputs, Objective) :-
    (   dcp_defined(model, 4)
    ->  call(model(Instance, Vars, Outputs, Given), user),
        dcp_check_objective(Given),
        Objective = Given
    ;   dcp_defined(model, 3)
    ->  call(model(Instance, Vars, Outputs), user),
        Objective = none
    ;   dcp_fail_with("The submission defines neither model/3 nor model/4")
    ),
    dcp_check_outputs(Outputs).

dcp_defined(Name, Arity) :-
    call(current_predicate(Name/Arity), user).

dcp_objective(min(Expression), min, Expression).
dcp_objective(max(Expression), max, Expression).

dcp_post(Constraint) :-
    call(Constraint, user).

dcp_check_objective(none) :- !.
dcp_check_objective(min(_)) :- !.
dcp_check_objective(max(_)) :- !.
dcp_check_objective(Other) :-
    dcp_fail_with("The objective must be min(Expr), max(Expr) or none, not %w", [Other]).

dcp_check_outputs(Outputs) :-
    (   is_list(Outputs), Outputs \== []
    ->  dcp_check_names(Outputs, [])
    ;   dcp_fail_with("Outputs must be a nonempty list of Name-Value pairs, not %w", [Outputs])
    ).

dcp_check_names([], _).
dcp_check_names([Pair|Rest], Seen) :-
    (   nonvar(Pair), Pair = Name-_, atom(Name)
    ->  true
    ;   dcp_fail_with("Each output must be Name-Value with an atom name, not %w", [Pair])
    ),
    (   memberchk(Name, Seen)
    ->  dcp_fail_with("The output %w is declared twice", [Name])
    ;   true
    ),
    dcp_check_names(Rest, [Name|Seen]).

% ---------------------------------------------------------------------------
% Output

% A solution counts once per distinct assignment of the declared outputs.
dcp_report_solution(Outputs) :-
    dcp_check_values(Outputs),
    getval(dcp_seen, Seen),
    (   memberchk(Outputs, Seen)
    ->  true
    ;   setval(dcp_seen, [Outputs|Seen]),
        write(dcp_protocol, "{\"type\": \"solution\", \"values\": {"),
        dcp_write_pairs(Outputs),
        write(dcp_protocol, "}}"),
        nl(dcp_protocol),
        flush(dcp_protocol),
        getval(dcp_count, Count),
        Next is Count + 1,
        setval(dcp_count, Next)
    ).

dcp_check_values([]).
dcp_check_values([Name-Value|Rest]) :-
    dcp_check_value(Name, Value),
    dcp_check_values(Rest).

dcp_check_value(Name, Value) :-
    (   var(Value)
    ->  dcp_fail_with("Declared output %w was left unbound by labelling", [Name])
    ;   integer(Value)
    ->  true
    ;   ( Value == true ; Value == false )
    ->  true
    ;   is_list(Value)
    ->  dcp_check_elements(Name, Value)
    ;   dcp_fail_with("Declared output %w must hold integers or Booleans, found %w", [Name, Value])
    ).

dcp_check_elements(_, []).
dcp_check_elements(Name, [Value|Rest]) :-
    dcp_check_value(Name, Value),
    dcp_check_elements(Name, Rest).

dcp_write_pairs([]).
dcp_write_pairs([Name-Value|Rest]) :-
    dcp_json_string(Name),
    write(dcp_protocol, ": "),
    dcp_write_value(Value),
    (   Rest == []
    ->  true
    ;   write(dcp_protocol, ", "),
        dcp_write_pairs(Rest)
    ).

dcp_write_value(Value) :-
    (   is_list(Value)
    ->  write(dcp_protocol, "["),
        dcp_write_elements(Value),
        write(dcp_protocol, "]")
    ;   write(dcp_protocol, Value)
    ).

dcp_write_elements([]).
dcp_write_elements([Value|Rest]) :-
    dcp_write_value(Value),
    (   Rest == []
    ->  true
    ;   write(dcp_protocol, ", "),
        dcp_write_elements(Rest)
    ).

dcp_status(Status, Detail, Seconds) :-
    write(dcp_protocol, "{\"type\": \"status\", \"status\": "),
    dcp_json_string(Status),
    write(dcp_protocol, ", \"detail\": "),
    dcp_json_string(Detail),
    (   number(Seconds)
    ->  printf(dcp_protocol, ", \"solve_seconds\": %w", [Seconds])
    ;   true
    ),
    write(dcp_protocol, "}"),
    nl(dcp_protocol),
    flush(dcp_protocol).

dcp_json_string(Text) :-
    text_to_string(Text, String),
    string_list(String, Codes),
    put(dcp_protocol, 34),
    dcp_json_codes(Codes),
    put(dcp_protocol, 34).

dcp_json_codes([]).
dcp_json_codes([Code|Rest]) :-
    (   Code == 34 -> write(dcp_protocol, "\\\"")
    ;   Code == 92 -> write(dcp_protocol, "\\\\")
    ;   Code == 10 -> write(dcp_protocol, "\\n")
    ;   Code < 32 -> put(dcp_protocol, 32)
    ;   put(dcp_protocol, Code)
    ),
    dcp_json_codes(Rest).

% ---------------------------------------------------------------------------
% Budget and failure reporting. Every outcome leaves exactly one status record.

dcp_bounded(Deadline, Goal, Where) :-
    statistics(session_time, Now),
    Left is max(0.001, Deadline - Now),
    timeout(Goal, Left, throw(dcp_timeout(Where))).

dcp_fail_with(Format) :-
    throw(submission_error(Format)).

dcp_fail_with(Format, Arguments) :-
    sprintf(Message, Format, Arguments),
    throw(submission_error(Message)).

dcp_messages_text(Text) :-
    flush(dcp_messages),
    open('/tmp/dcp_messages.txt', read, In),
    read_string(In, "", _, Text),
    close(In).

% The last part of the messages, which holds ECLiPSe's own account of an error.
dcp_messages_tail(Tail) :-
    dcp_messages_text(Text),
    string_length(Text, Length),
    (   Length > 2000
    ->  Start is Length - 2000,
        substring(Text, Start, 2000, _, Tail)
    ;   Tail = Text
    ).

dcp_report(dcp_timeout(Where)) :- !,
    sprintf(Detail, "The execution budget ran out during %w", [Where]),
    dcp_status(timeout, Detail, none).
dcp_report(submission_error(Message)) :- !,
    dcp_status(error, Message, none).
dcp_report(abort) :- !,
    % ECLiPSe's default error handler printed the message and then aborted.
    dcp_messages_tail(Tail),
    dcp_status(error, Tail, none).
dcp_report(Ball) :-
    sprintf(Message, "The submission threw %w", [Ball]),
    dcp_status(error, Message, none).
