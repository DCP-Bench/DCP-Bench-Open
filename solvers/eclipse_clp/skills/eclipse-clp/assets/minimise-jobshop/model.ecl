% Job shop: 3 jobs, 3 machines, each job visits its machines in the given order.
% Minimise the makespan. One disjunctive/2 per machine (library ic_edge_finder).
:- lib(ic).
:- lib(ic_edge_finder).
:- lib(branch_and_bound).

% job(Name, [task(Machine, Duration), ...])
job(j1, [task(1,3), task(2,2), task(3,2)]).
job(j2, [task(2,2), task(1,1), task(3,4)]).
job(j3, [task(3,4), task(2,3), task(1,2)]).

% One start variable per task: t(Machine, Start, Duration) records.
make_records([], _, []).
make_records([task(M,D)|Rest], H, [t(M,S,D)|Ts]) :-
    S :: 0..H,
    make_records(Rest, H, Ts).

% Tasks of one job follow each other.
chain([_]).
chain([t(_,S1,D1), t(M2,S2,D2)|Rest]) :-
    S1 + D1 #=< S2,
    chain([t(M2,S2,D2)|Rest]).

% Start and duration lists of the records that use machine M.
% Plain recursion, not findall/3: findall would copy the variables.
on_machine(_, [], [], []).
on_machine(M, [t(M1,S,D)|Ts], Ss, Ds) :-
    ( M1 == M -> Ss = [S|Ss1], Ds = [D|Ds1] ; Ss = Ss1, Ds = Ds1 ),
    on_machine(M, Ts, Ss1, Ds1).

main :-
    findall(Tasks, job(_, Tasks), Jobs),
    ( foreach(Ts, Jobs), fromto(0, H0, H1, Horizon) do
        ( foreach(task(_,D), Ts), fromto(H0, A, B, H1) do B is A + D )
    ),
    % records, precedences, and the end of each job
    ( foreach(Ts, Jobs), foreach(Recs, JobRecs), foreach(End, Ends), param(Horizon) do
        make_records(Ts, Horizon, Recs),
        chain(Recs),
        last_end(Recs, End)
    ),
    flatten(JobRecs, All),
    % no overlap on each machine
    ( for(M, 1, 3), param(All) do
        on_machine(M, All, Ss, Ds),
        disjunctive(Ss, Ds)
    ),
    Makespan #= max(Ends),
    ( foreach(t(_,S,_), All), foreach(S, Starts) do true ),
    bb_min(search(Starts, 0, smallest, indomain_min, complete, []), Makespan,
           bb_options{report_success:true/0, report_failure:true/0}),
    printf("Makespan: %d%n", [Makespan]),
    ( foreach(Recs, JobRecs), count(J, 1, _) do
        ( foreach(t(M,S,D), Recs), foreach(Text, Texts) do
            concat_string([M, ":", S, "+", D], Text)
        ),
        printf("job %d: %w%n", [J, Texts])
    ).

last_end([t(_,S,D)], S + D) :- !.
last_end([_|Rest], End) :- last_end(Rest, End).
