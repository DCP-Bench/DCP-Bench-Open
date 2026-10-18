% Permutation flowshop scheduling: n jobs must be processed on m machines in
% series, all jobs in the same machine order (machine 1 to machine m). Each
% machine processes one job at a time. The time needed by job j on machine m is
% ProcesTime_{j,m}. Find the sequence of jobs that minimises the makespan, the
% time when all jobs have been processed.

:- lib(ic).
:- lib(listut).

model(Instance, Seq, [makespan-Mk], min(Mk)) :-
    memberchk(process_time-PT, Instance),
    length(PT, N),
    PT = [Row1|_],
    length(Row1, M),
    ( foreach(Row, PT), fromto(0, A, B, Ub) do
          ( foreach(X, Row), fromto(A, A1, A2, B) do A2 is A1 + X )
    ),
    % The sequence: Seq[K] is the job (1-based) in position K.
    % Every job takes exactly one position.
    length(Seq, N),
    Seq :: 1..N,
    alldifferent(Seq),
    % Processing time of each job on each machine, indexed by job.
    columns(1, M, PT, Cols),
    % Completion times: row K holds the completion time of the job in
    % position K on machines 1..M.
    length(Zeros, M),
    ( foreach(Z, Zeros) do Z = 0 ),
    schedule(Seq, Cols, M, Ub, Zeros, Final),
    nth1(M, Final, Mk),
    Mk :: 0..Ub.

search_goal(Seq) :-
    search(Seq, 0, first_fail, indomain_min, complete, []).

% Col_m lists the processing time of every job (by job index) on machine m.
columns(M, Mmax, _, []) :-
    M > Mmax, !.
columns(M, Mmax, PT, [Col|Cols]) :-
    ( foreach(R, PT), foreach(V, Col), param(M) do nth1(M, R, V) ),
    M1 is M + 1,
    columns(M1, Mmax, PT, Cols).

% Process the positions in order. Prev is the completion row of the previous
% position (zeros before the first one).
schedule([], _, _, _, Prev, Prev).
schedule([S|Ss], Cols, M, Ub, Prev, Final) :-
    row(1, M, S, Cols, Ub, Prev, 0, Row),
    schedule(Ss, Cols, M, Ub, Row, Final).

% The job in this position starts on machine Mc when the machine is free
% (the previous job left it, Up) and the job has left machine Mc-1 (Left).
row(Mc, M, _, _, _, _, _, []) :-
    Mc > M, !.
row(Mc, M, S, Cols, Ub, Prev, Left, [C|Cs]) :-
    nth1(Mc, Cols, Col),
    element(S, Col, P),
    nth1(Mc, Prev, Up),
    C :: 0..Ub,
    C #= max(Up, Left) + P,
    Mc1 is Mc + 1,
    row(Mc1, M, S, Cols, Ub, Prev, C, Cs).
