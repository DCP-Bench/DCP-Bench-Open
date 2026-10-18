% Set (card game): find three cards on the table that form a set.
%
% Three cards form a set when, for each of the four features, the three cards
% show that feature either all the same or all different. Each card has four
% features with three values each (1..3). The output is the 0-based indices of
% the three cards that form the winning set.

:- lib(ic).
:- lib(listut).

model(Instance, [I, J, K], [winning_cards-[I, J, K]]) :-
    memberchk(cards_data-Cards, Instance),
    length(Cards, N),

    % the winning set is three different cards on the table (0-based indices)
    [I, J, K] :: 0..N-1,
    alldifferent([I, J, K]),

    % element/3 is 1-based, so the 1-based positions of the three cards
    I1 #= I + 1,
    J1 #= J + 1,
    K1 #= K + 1,

    % one column per feature: the value of that feature on every card
    ( for(F, 1, 4), foreach(Col, Cols), param(Cards) do
        ( foreach(Card, Cards), foreach(V, Col), param(F) do
            nth1(F, Card, V)
        )
    ),

    % for each feature, the three cards show it all the same or all different
    ( foreach(Col, Cols), param(I1, J1, K1) do
        element(I1, Col, A),
        element(J1, Col, B),
        element(K1, Col, C),
        ( (A #= B) and (B #= C) )
            or ( (A #\= B) and (B #\= C) and (A #\= C) )
    ).
