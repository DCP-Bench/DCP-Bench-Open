% Climbing stairs: climb a stair of n steps with a number of steps at a time,
% within a given range [m1, m2]. Print the number of steps (steps) taken at each
% move as a list of n integers, where each integer is between m1 and m2, or 0 if
% no steps are taken at that move, i.e. after we reach the top of the stair.

:- lib(ic).
:- lib(listut).

model(Instance, Steps, [steps-Steps]) :-
    memberchk(n-N, Instance),
    memberchk(m1-M1, Instance),
    memberchk(m2-M2, Instance),
    length(Steps, N),

    % Each move takes m1 to m2 steps at a time, or 0 once the top is reached.
    ( foreach(S, Steps), param(M1, M2) do
        S :: 0..M2,
        ( for(K, 1, M1 - 1), param(S) do S #\= K )
    ),

    % The moves climb the stair of n steps in total.
    sum(Steps) #= N,

    % Once the top is reached, every later move is 0: a move is 0 only when the
    % moves before it already add up to n.
    prefix_constraints(Steps, 0, N).

% prefix_constraints(+Moves, +Climbed, +N): Climbed is the steps climbed before
% the first move of Moves.
prefix_constraints([], _, _).
prefix_constraints([S|Ss], Climbed, N) :-
    (S #= 0) => (Climbed #= N),
    NewClimbed #= Climbed + S,
    prefix_constraints(Ss, NewClimbed, N).
