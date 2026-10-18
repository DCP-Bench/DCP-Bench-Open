% Nontransitive dice (big_bang2): five dice with six integer faces each, face values 1..12.
% Rows of the output: Rock, Paper, Scissors, Lizard, Spock.
% Die A beats die B when A has a strictly larger face value than B in more than half of all
% possible pairs of faces, that is in at least 19 of the 36 pairs.

:- lib(ic).

model(_Instance, Vars, [dice-Dice]) :-
    Dice = [Rock, Paper, Scissors, Lizard, Spock],
    % Each die has six integer-valued faces, each face value between 1 and 12 inclusive.
    ( foreach(Row, Dice) do length(Row, 6), Row :: 1..12 ),

    % Per die: Counts[V] = number of faces showing V, Below[V] = number of faces below V,
    % Close = closeness of the face sum to its mean 6 * 6.5 (search guide only).
    die_view(Rock, CR, BR, ClR),
    die_view(Paper, CP, BP, ClP),
    die_view(Scissors, CS, BS, ClS),
    die_view(Lizard, CL, BL, ClL),
    die_view(Spock, CSp, BSp, ClSp),

    % The ten beats relationships between the choices:
    % Rock crushes Scissors, Rock crushes Lizard, Paper covers Rock, Paper disproves Spock,
    % Scissors cuts Paper, Scissors decapitate Lizard, Lizard eats Paper, Lizard poisons Spock,
    % Spock vaporizes Rock, Spock smashes Scissors.
    % A beats B: A has a strictly larger face than B in more than half of the 36 face pairs.
    wins(CR, BS), wins(CR, BL),
    wins(CP, BR), wins(CP, BSp),
    wins(CS, BP), wins(CS, BL),
    wins(CL, BP), wins(CL, BSp),
    wins(CSp, BR), wins(CSp, BS),

    % Labelling order: per die its closeness, then its counts; then all faces.
    flatten([[ClR|CR], [ClS|CS], [ClP|CP], [ClL|CL], [ClSp|CSp], Dice], Vars).

die_view(Row, Counts, Below, Close) :-
    length(Counts, 12),
    length(Below, 12),
    ( for(V, 1, 12), foreach(C, Counts), param(Row) do
        ( foreach(F, Row), foreach(B, Bs), param(V) do B #= (F #= V) ),
        C :: 0..6,
        C #= sum(Bs)
    ),
    sum(Counts) #= 6,
    ( for(V, 1, 12), foreach(C, Counts), foreach(T, Ts) do T = V * C ),
    S #= sum(Ts),
    ( foreach(C, Counts), foreach(B, Below), fromto(0, Acc, Acc1, _) do
        B :: 0..6, B #= Acc, Acc1 #= Acc + C
    ),
    Close :: 0..33,
    Close #= 33 - abs(S - 39).

% Die W beats die L: the pairs won are the sum over values V of Counts_W[V] * Below_L[V].
wins(CW, BL) :-
    ( foreach(C, CW), foreach(B, BL), foreach(P, Ps) do
        P :: 0..36, P #= C * B
    ),
    sum(Ps) #>= 19.

search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_max, complete, []).
