:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% The card game Set: among the cards on the table find three that form a set,
% that is, for each of the four features (number, fill, colour, shape) the three
% cards either all show the same value or all show different values.
model(Instance, Winning, [winning_cards-Winning]) :-
    Cards = Instance.cards_data,   % each card is [number, fill, colour, shape]
    length(Cards, NCards),
    Top is NCards - 1,

    % Winning = the indices (from 0) of the three chosen cards, all different
    length(Winning, 3),
    Winning ins 0..Top,
    all_distinct(Winning),

    % for each feature, the three chosen cards show all the same value or all different values
    transpose(Cards, Features),
    maplist({Winning}/[Table]>>(maplist({Table}/[Index, Value]>>(Position #= Index + 1, element(Position, Table, Value)),
                                        Winning, [A, B, C]),
                                ((A #= B #/\ B #= C) #\/ (A #\= B #/\ B #\= C #/\ A #\= C))),
            Features).
