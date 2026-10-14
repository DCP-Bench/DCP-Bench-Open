% The card game Set: among the cards on the table find three that form a set,
% that is, for each of the four features (number, fill, colour, shape) the three
% cards either all show the same value or all show different values.
% cards_data(C, F, V): card C shows value V for feature F (0 number, 1 fill, 2 colour, 3 shape).
card(C) :- cards_data(C,_,_).

% winning_cards(K, C): the K-th chosen card is card C; the three cards are different.
1 { winning_cards(K,C) : card(C) } 1 :- K = 0..2.
:- winning_cards(K1,C), winning_cards(K2,C), K1 < K2.

% shown(K, F, V): the K-th chosen card has value V for feature F.
shown(K,F,V) :- winning_cards(K,C), cards_data(C,F,V).

% The three values are all equal or all different: if two of the cards share a
% value, the third one shares it too.
:- shown(K1,F,V), shown(K2,F,V), K1 < K2, K3 = 0..2, K3 != K1, K3 != K2, not shown(K3,F,V).

#show winning_cards/2.
