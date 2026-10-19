% Cumulative resource: six tasks share a resource of capacity 3.
% Minimise the makespan. cumulative/4 comes from ic_edge_finder (stronger
% propagation than ic_cumulative, same arguments).
:- lib(ic).
:- lib(ic_edge_finder).
:- lib(branch_and_bound).

% task(Name, Duration, Demand)
task(a, 3, 2).
task(b, 2, 1).
task(c, 2, 2).
task(d, 4, 1).
task(e, 3, 2).
task(f, 1, 3).

before(a, c).
before(b, d).

main :-
    findall(N-D-R, task(N, D, R), Tasks),
    ( foreach(_-D-_, Tasks), fromto(0, A, B, Horizon) do B is A + D ),
    ( foreach(N-D-R, Tasks), foreach(N-S, Starts), foreach(D, Ds), foreach(R, Rs),
      foreach(S, Ss), param(Horizon) do
        S :: 0..Horizon
    ),
    % precedences: the first task ends before the second starts
    % (a failure-driven loop would undo each constraint it posts, so use foreach)
    findall(X-Y, before(X, Y), Precs),
    ( foreach(X-Y, Precs), param(Starts, Tasks) do
        memberchk(X-SX, Starts), memberchk(Y-SY, Starts),
        memberchk(X-DX-_, Tasks),
        SX + DX #=< SY
    ),
    cumulative(Ss, Ds, Rs, 3),
    % makespan: at least every end time
    ( foreach(S, Ss), foreach(D, Ds), foreach(E, Ends) do E = S + D ),
    Makespan #= max(Ends),
    bb_min(search(Ss, 0, smallest, indomain_min, complete, []), Makespan,
           bb_options{report_success:true/0, report_failure:true/0}),
    printf("Makespan: %d%n", [Makespan]),
    ( foreach(N-S, Starts) do printf("%w starts at %d%n", [N, S]) ).
