% Water bucket (CSPLib 018). Three buckets with capacities 8, 5 and 3 pints.
% The 8-pint bucket starts full, the other two are empty. Pour water between
% buckets until the 8-pint bucket holds 4 pints and the 5-pint bucket holds 4.
% Minimise the number of transfers (cost). The sequence lists the initial state,
% then the state after each transfer, and is padded after the goal state.

:- lib(ic).
:- lib(lists).

model(Instance, Vars, Outputs, min(Cost)) :-
    memberchk(capacities-Caps, Instance),
    memberchk(initial_state-Init, Instance),
    memberchk(goal_state-Goal, Instance),
    memberchk('MAX_STEPS'-Max, Instance),
    memberchk('PADDING_VALUE'-Pad, Instance),
    length(States, Max),
    % Each bucket holds between 0 and its capacity pints.
    ( foreach(St, States), param(Caps) do
        St = [A,B,C], Caps = [Ca,Cb,Cc],
        A :: 0..Ca, B :: 0..Cb, C :: 0..Cc
    ),
    % The first state is the initial state.
    States = [S0|_],
    ( foreach(X, S0), foreach(V, Init) do X #= V ),
    % Cost is the number of transfers; transfers 0 .. Cost-1 are performed.
    Cost :: 0..Max-1,
    % Each transfer pours water from one bucket into another.
    pours(States, 0, Caps, Cost, Fs, Tos),
    % After the goal state, the states are fixed to 0 (their output is padding).
    zero_after(States, 0, Cost),
    % The goal state is reached after Cost transfers.
    goal_at(States, 0, Goal, Cost),
    % Outputs: states up to the goal, padding afterwards.
    output_rows(States, 0, Cost, Pad, Caps, Seq),
    flatten(States, FlatStates),
    append([Cost|Fs], Tos, Head),
    append(Head, FlatStates, Vars),
    Outputs = [cost-Cost, sequence-Seq].

% Transfers between consecutive states.
pours([_], _, _, _, [], []).
pours([S,N|Rest], Idx, Caps, Cost, [F|Fs], [To|Tos]) :-
    pour(Idx, S, N, Caps, Cost, F, To),
    Idx1 is Idx + 1,
    pours([N|Rest], Idx1, Caps, Cost, Fs, Tos).

% A transfer from bucket F to bucket To: the amount is what the source holds or
% what the target can take, whichever is smaller. Transfers after the cost are
% not used, so their buckets are fixed.
pour(Idx, S, N, Caps, Cost, F, To) :-
    S = [S1,S2,S3], N = [N1,N2,N3],
    F :: 1..3, To :: 1..3,
    F #\= To,
    element(F, S, SrcV),
    element(To, S, DstV),
    element(To, Caps, CapTo),
    Amt #>= 0, Amt #=< CapTo,
    Amt #= min(SrcV, CapTo - DstV),
    F1 #= (F #= 1), F2 #= (F #= 2), F3 #= (F #= 3),
    T1 #= (To #= 1), T2 #= (To #= 2), T3 #= (To #= 3),
    % Water moves out of F and into To.
    (Idx #< Cost) => (N1 #= S1 - F1*Amt + T1*Amt),
    (Idx #< Cost) => (N2 #= S2 - F2*Amt + T2*Amt),
    (Idx #< Cost) => (N3 #= S3 - F3*Amt + T3*Amt),
    (Idx #>= Cost) => (F #= 1),
    (Idx #>= Cost) => (To #= 2).

% States after the goal state are fixed to 0.
zero_after([], _, _).
zero_after([S|Ss], Idx, Cost) :-
    S = [A,B,C],
    (Idx #> Cost) => (A #= 0),
    (Idx #> Cost) => (B #= 0),
    (Idx #> Cost) => (C #= 0),
    Idx1 is Idx + 1,
    zero_after(Ss, Idx1, Cost).

% The state after Cost transfers is the goal state.
goal_at([], _, _, _).
goal_at([S|Ss], Idx, Goal, Cost) :-
    S = [A,B,C], Goal = [GA,GB,GC],
    (Cost #= Idx) => (A #= GA),
    (Cost #= Idx) => (B #= GB),
    (Cost #= Idx) => (C #= GC),
    Idx1 is Idx + 1,
    goal_at(Ss, Idx1, Goal, Cost).

% Output row per state: the state up to the goal, the padding value afterwards.
output_rows([], _, _, _, _, []).
output_rows([S|Ss], Idx, Cost, Pad, Caps, [Row|Rows]) :-
    S = [S1,S2,S3], Row = [O1,O2,O3], Caps = [Ca,Cb,Cc],
    O1 :: Pad..Ca, O2 :: Pad..Cb, O3 :: Pad..Cc,
    (Idx #=< Cost) => (O1 #= S1),
    (Idx #=< Cost) => (O2 #= S2),
    (Idx #=< Cost) => (O3 #= S3),
    (Idx #> Cost) => (O1 #= Pad),
    (Idx #> Cost) => (O2 #= Pad),
    (Idx #> Cost) => (O3 #= Pad),
    Idx1 is Idx + 1,
    output_rows(Ss, Idx1, Cost, Pad, Caps, Rows).
