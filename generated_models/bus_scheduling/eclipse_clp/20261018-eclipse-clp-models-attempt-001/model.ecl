% Bus scheduling (Progress City): minimise the number of buses for a
% day split into successive 4-hour intervals. Demand per interval is
% given by the instance (demands). Each bus operates 8 successive hours,
% that is two successive intervals, and the day wraps around.
% x[i] is the number of buses that start in interval i.
:- lib(ic).
:- lib(listut).

model(Instance, X, [x-X], min(Cost)) :-
    memberchk(demands-Demands, Instance),
    length(Demands, N),
    length(X, N),
    ( foreach(D, Demands), fromto(0, A, B, MaxD) do B is max(A, D) ),
    X :: 0..MaxD,

    % The buses on duty in interval i are those that started in interval i
    % or in the interval before it (cyclically); together they meet the demand.
    ( for(I, 0, N-1), param(X, Demands, N) do
        nth0(I, Demands, Di),
        Prev is (I + N - 1) mod N,
        nth0(Prev, X, XPrev),
        nth0(I, X, XI),
        XI + XPrev #>= Di
    ),

    % The objective is the total number of buses.
    Cost #= sum(X).
