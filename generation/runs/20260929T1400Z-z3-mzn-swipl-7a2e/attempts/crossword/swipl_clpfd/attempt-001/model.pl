:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Crossword: pick 8 different words from a list of 15 to fill the 8 numbered
% slots of a small crossword grid so that every place where two slots cross
% holds the same letter in both words.
%
% The puzzle itself is fixed by the problem, so its data is mirrored here.
% The words, sorted longest first and then alphabetically.
words(['HOSES', 'LASER', 'SAILS', 'SHEET', 'STEER',
       'HEEL', 'HIKE', 'KEEL', 'KNOT', 'LINE',
       'AFT', 'ALE', 'EEL', 'LEE', 'TIE']).
% crossing(SlotA, PositionInA, SlotB, PositionInB), slots numbered from 0 and positions from 1
crossings([[0, 3, 1, 1], [0, 5, 2, 1], [3, 2, 1, 3], [3, 3, 4, 1], [3, 4, 2, 3], [6, 1, 1, 4],
           [6, 2, 4, 2], [6, 3, 2, 4], [7, 1, 5, 2], [7, 3, 1, 5], [7, 4, 4, 3], [7, 5, 2, 5]]).

model(_Instance, E, ['E'-E]) :-
    words(Words),
    crossings(Crossings),
    length(Words, NWords),
    Top is NWords - 1,

    % E[s] = the word (index from 0 in the list) placed in slot s; all slots get different words
    length(E, 8),
    E ins 0..Top,
    all_distinct(E),

    % the letters of every word as numbers (A=1 .. Z=26), padded with 0 to length 5
    maplist([Word, Letters]>>(atom_codes(Word, Codes),
                              maplist([Code, Number]>>(Number is Code - 64), Codes, Numbers),
                              length(Numbers, Length), Padding is 5 - Length,
                              length(Zeros, Padding), maplist(=(0), Zeros),
                              append(Numbers, Zeros, Letters)),
            Words, Table),

    % where two slots cross, the two words show the same letter: the letter at a
    % position is read from the table with element/3, which counts from 1
    maplist({E, Table}/[[SlotA, PosA, SlotB, PosB]]>>(
                letter(E, Table, SlotA, PosA, LetterA),
                letter(E, Table, SlotB, PosB, LetterB),
                LetterA #= LetterB), Crossings).

% letter(+E, +Table, +Slot, +Position, -Letter)
letter(E, Table, Slot, Position, Letter) :-
    nth0(Slot, E, Word),
    maplist({Position}/[Row, Cell]>>nth1(Position, Row, Cell), Table, Column),
    Index #= Word + 1,
    element(Index, Column, Letter).
