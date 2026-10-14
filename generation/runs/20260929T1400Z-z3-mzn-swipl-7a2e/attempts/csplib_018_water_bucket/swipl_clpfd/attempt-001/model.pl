:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Water bucket: three buckets with given capacities start in the initial state
% and water is poured from one bucket into another (until the source is empty
% or the target full). Reach the goal state with as few pourings as possible.
% The states are listed one per step in a fixed-length sequence, padded after the goal.
model(Instance, Vars, [cost-Cost, sequence-Sequence], min(Cost)) :-
    Capacities = Instance.capacities,
    Initial = Instance.initial_state,
    Goal = Instance.goal_state,
    MaxSteps = Instance.'MAX_STEPS',        % length of the output sequence
    Pad = Instance.'PADDING_VALUE',         % marks the unused steps after the goal
    sum_list(Initial, TotalWater),          % the water is only moved around, never lost
    length(Capacities, NBuckets),

    % every state within the capacities that holds all the water, and every legal
    % pouring as a (state before, state after) row, all ground data
    Capacities = [Cap1, Cap2, Cap3],
    findall(State, (between(0, Cap1, A), between(0, Cap2, B), C is TotalWater - A - B,
                    C >= 0, C =< Cap3, State = [A, B, C]), States),
    findall(Row, (member(State, States), between(1, 3, Source), between(1, 3, Target), Source =\= Target,
                  pour(State, Capacities, Source, Target, After), Row = [State, After]),
            PouringList),
    % one step is a pouring from a state that is not the goal, a move from the goal
    % into the padding, or padding after padding
    length(PadRow, NBuckets), maplist(=(Pad), PadRow),
    findall(Flat, (member([Before, After], PouringList), Before \== Goal, append(Before, After, Flat)), Pourings),
    append(Goal, PadRow, GoalToPad),
    append(PadRow, PadRow, PadToPad),
    sort([GoalToPad, PadToPad|Pourings], Transitions),

    % Sequence[t] = the amounts in the buckets after t pourings, or padding
    length(Sequence, MaxSteps),
    maplist({NBuckets, Pad, TotalWater}/[Step]>>(length(Step, NBuckets), Step ins Pad..TotalWater), Sequence),

    % the sequence starts with the initial state
    Sequence = [Initial|_],

    % each step follows from the one before by a legal pouring; the goal is
    % followed by padding, and once padding starts it goes on
    successive(Sequence, Transitions),
    % the last step is the goal or padding, so the goal has been reached at some point
    last(Sequence, LastStep),
    tuples_in([LastStep], [Goal, PadRow]),

    % cost = number of pourings = number of states before the padding starts, minus one
    maplist({Pad}/[[First|_], Used]>>(Used #<==> (First #\= Pad)), Sequence, Uses),
    sum(Uses, #=, Used),
    Cost #= Used - 1,
    Cost in 0..MaxSteps,
    append(Sequence, Cells),
    append(Cells, [Cost|Uses], Vars).

% pour(+State, +Capacities, +Source, +Target, -After): pour bucket Source into
% bucket Target until the source is empty or the target full (only when water moves)
pour(State, Capacities, Source, Target, After) :-
    nth1(Source, State, InSource),
    nth1(Target, State, InTarget),
    nth1(Target, Capacities, TargetCapacity),
    Amount is min(InSource, TargetCapacity - InTarget),
    Amount > 0,
    findall(Value, (nth1(Bucket, State, Old),
                    ( Bucket =:= Source -> Value is Old - Amount
                    ; Bucket =:= Target -> Value is Old + Amount
                    ; Value = Old )), After).

% every step is followed by one that makes an allowed transition
successive([_], _).
successive([Before, After|Rest], Transitions) :-
    append(Before, After, Both),
    tuples_in([Both], Transitions),
    successive([After|Rest], Transitions).
