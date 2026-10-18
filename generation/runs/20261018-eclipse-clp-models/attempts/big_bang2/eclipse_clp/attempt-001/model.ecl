% Nontransitive dice (big_bang2): five dice with six integer faces each, face values 1..12.
% Dice are Rock, Paper, Scissors, Lizard, Spock (rows 0..4 of the output).
% Die A beats die B when A has a strictly larger face than B in more than half of all
% pairs of faces, that is in at least 19 of the 36 pairs.

:- lib(ic).

model(_Instance, Vars, [dice-Dice]) :-
    Dice = [Rock, Paper, Scissors, Lizard, Spock],
    ( foreach(Row, Dice) do length(Row, 6) ),
    flatten(Dice, Faces),
    Faces :: 1..12,

    % The ten beats relationships between the choices:
    % Rock crushes Scissors, Rock crushes Lizard, Paper covers Rock, Paper disproves Spock,
    % Scissors cuts Paper, Scissors decapitate Lizard, Lizard eats Paper, Lizard poisons Spock,
    % Spock vaporizes Rock, Spock smashes Scissors.
    % Each beats relationship means the winner has more than half of the 36 face pairs.
    beats(Rock, Scissors, F1),
    beats(Rock, Lizard, F2),
    beats(Paper, Rock, F3),
    beats(Paper, Spock, F4),
    beats(Scissors, Paper, F5),
    beats(Scissors, Lizard, F6),
    beats(Lizard, Paper, F7),
    beats(Lizard, Spock, F8),
    beats(Spock, Rock, F9),
    beats(Spock, Scissors, F10),
    flatten([F1, F2, F3, F4, F5, F6, F7, F8, F9, F10], Flags),
    Flags :: 0..1,

    % Label the faces and the comparison flags together.
    append(Faces, Flags, Vars).

% Die A beats die B: at least 19 of the 36 face pairs have A's face strictly larger.
beats(A, B, Flags) :-
    gt_flags(A, B, Rows),
    flatten(Rows, Flags),
    sum(Flags) #>= 19.

% One flag per pair of faces (X from A, Y from B): flag is 1 exactly when X > Y.
gt_flags(As, Bs, Rows) :-
    ( foreach(X, As), param(Bs), foreach(Row, Rows) do
        ( foreach(Y, Bs), param(X), foreach(G, Row) do
            G #= (X #> Y)
        )
    ).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
