% Nontransitive dice (big_bang2): five dice with six integer faces each, face values 1..12.
% Rows of the output: Rock, Paper, Scissors, Lizard, Spock.
% Die A beats die B when A has a strictly larger face value than B in more than half of all
% possible pairs of faces, that is in at least 19 of the 36 pairs.

:- lib(ic).

model(_Instance, Vars, [dice-Dice]) :-
    Dice = [Rock, Paper, Scissors, Lizard, Spock],
    ( foreach(Row, Dice) do length(Row, 6) ),
    flatten(Dice, Faces),
    Faces :: 1..12,

    % Per die: how many faces show each value 1..12 (counts), and how many faces are
    % strictly below each value (below). These are functions of the faces.
    face_counts(Rock, CR), face_counts(Paper, CP), face_counts(Scissors, CS),
    face_counts(Lizard, CL), face_counts(Spock, CSp),
    below_counts(CR, BR), below_counts(CP, BP), below_counts(CS, BS),
    below_counts(CL, BL), below_counts(CSp, BSp),

    % The ten beats relationships between the choices:
    % Rock crushes Scissors, Rock crushes Lizard, Paper covers Rock, Paper disproves Spock,
    % Scissors cuts Paper, Scissors decapitate Lizard, Lizard eats Paper, Lizard poisons Spock,
    % Spock vaporizes Rock, Spock smashes Scissors.
    % Each beats relationship means the winner has at least 19 of the 36 face pairs.
    wins(CR, BS), wins(CR, BL),
    wins(CP, BR), wins(CP, BSp),
    wins(CS, BP), wins(CS, BL),
    wins(CL, BP), wins(CL, BSp),
    wins(CSp, BR), wins(CSp, BS),

    % Search guide: a closeness measure per die (face sum near the mean 6 * 6.5 = 39).
    closeness(Rock, ClR), closeness(Scissors, ClS), closeness(Paper, ClP),
    closeness(Lizard, ClL), closeness(Spock, ClSp),

    % Labelling order: per die its closeness, then its counts; then all faces.
    flatten([[ClR|CR], [ClS|CS], [ClP|CP], [ClL|CL], [ClSp|CSp], Faces], Vars).

% Counts: Counts[V] is the number of faces of Row showing the value V (V = 1..12).
face_counts(Row, Counts) :-
    length(Counts, 12),
    Counts :: 0..6,
    sum(Counts) #= 6,
    ( for(V, 1, 12), foreach(C, Counts), param(Row) do
        count_value(Row, V, C)
    ).

count_value(Row, V, C) :-
    ( foreach(F, Row), foreach(B, Bs), param(V) do
        B #= (F #= V)
    ),
    sum(Bs) #= C.

% Below[V] is the number of faces with a value strictly smaller than V (V = 1..12).
below_counts(Counts, Below) :-
    below_counts(Counts, 0, Below).

below_counts([], _, []).
below_counts([C|Cs], Acc, [Acc|Bs]) :-
    Acc1 #= Acc + C,
    below_counts(Cs, Acc1, Bs).

% Die W beats die L when W has at least 19 of the 36 face pairs with a strictly larger face.
% For each value V of a face of W, the faces of L below V give the pairs won:
% sum over V of Counts_W[V] * Below_L[V].
wins(CW, BL) :-
    ( foreach(C, CW), foreach(B, BL), foreach(P, Ps) do
        P #= C * B
    ),
    sum(Ps) #>= 19.

% Closeness of the face sum to its mean (39); used only to order the search.
closeness(Row, Cl) :-
    S #= sum(Row),
    S :: 6..72,
    Cl :: 0..33,
    Cl #= 33 - abs(S - 39).

search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_max, complete, []).
