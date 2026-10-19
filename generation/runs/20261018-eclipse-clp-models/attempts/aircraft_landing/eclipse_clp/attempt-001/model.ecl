% Aircraft landing problem: n aircraft land on one runway in a fixed sequence (index order).
% Each aircraft i lands at time x_i; the objective is the total penalty for landing
% before or after its target time, minimised subject to time windows and separations.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [landing_times-Xs, total_penalty-Total], min(Total)) :-
    memberchk(earliest_landing-Es, Instance),
    memberchk(latest_landing-Ls, Instance),
    memberchk(target_landing-Ts, Instance),
    memberchk(penalty_before-PBs, Instance),
    memberchk(penalty_after-PAs, Instance),
    memberchk(separation_time-Seps, Instance),
    length(Es, N),
    length(Xs, N),
    length(Ps, N),

    % each aircraft lands within its time window [earliest_landing, latest_landing]
    ( foreach(X, Xs), foreach(E, Es), foreach(L, Ls) do
        X :: E..L
    ),

    % minimum separation between the landings of any two aircraft, in the fixed sequence:
    % for all i < j, landing j is at least separation_time[i][j] after landing i
    ( for(I, 1, N), param(Xs, Seps, N) do
        nth1(I, Xs, XI),
        nth1(I, Seps, Row),
        I1 is I + 1,
        ( for(J, I1, N), param(Xs, Row, XI) do
            nth1(J, Xs, XJ),
            nth1(J, Row, S),
            XJ #>= XI + S
        )
    ),

    % penalty for landing before the target time (penalty_before per unit early) or
    % after it (penalty_after per unit late); zero on the target
    ( foreach(P, Ps), foreach(X, Xs), foreach(T, Ts), foreach(L, Ls), foreach(PB, PBs), foreach(PA, PAs) do
        pen_domain(P, PB, PA, T, L),
        P #>= PB * (T - X),
        P #>= PA * (X - T),
        P #>= 0
    ),

    % total penalty is the sum over all aircraft
    Total #= sum(Ps),

    append(Xs, Ps, Vars).

% the penalty of an aircraft is at most penalty_before * target + penalty_after * latest,
% since its landing time lies in [0, latest]
pen_domain(P, PB, PA, T, L) :-
    Hi is PB * T + PA * L,
    P :: 0..Hi.
