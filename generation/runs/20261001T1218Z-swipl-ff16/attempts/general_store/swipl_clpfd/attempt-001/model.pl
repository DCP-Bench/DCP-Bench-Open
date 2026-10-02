:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% General store (cryptarithm): each letter stands for a different digit. Sixteen
% words, read as numbers, add up to ALLWOOL. Find the digit of every letter.
% The problem has no instance data; the words below are the sign in the
% statement. As in the reference, a word may start with the digit 0.
model(_Instance, Vars, ['A'-A, 'B'-B, 'C'-C, 'E'-E, 'H'-H, 'L'-L, 'O'-O, 'P'-P, 'S'-S, 'W'-W]) :-
    Letters = ['C'-C, 'H'-H, 'E'-E, 'S'-S, 'A'-A, 'B'-B, 'O'-O, 'W'-W, 'P'-P, 'L'-L],
    pairs_values(Letters, Vars),

    % each letter is a digit, and different letters are different digits
    Vars ins 0..9,
    all_distinct(Vars),

    % the words above the line add up to the total
    Words = ['CHESS', 'CASH', 'BOWWOW', 'CHOPS', 'ALSOPS', 'PALEALE', 'COOL',
             'BASS', 'HOPS', 'ALES', 'HOES', 'APPLES', 'COWS', 'CHEESE',
             'CHSOAP', 'SHEEP'],
    maplist(word_value(Letters), Words, Values),
    sum(Values, #=, Total),
    word_value(Letters, 'ALLWOOL', Total).

% word_value(+Letters, +Word, ?Value): Value is the number the letters of Word
% spell, one digit per letter, most significant first.
word_value(Letters, Word, Value) :-
    atom_chars(Word, Chars),
    maplist(letter_digit(Letters), Chars, Digits),
    digits_value(Digits, 0, Value).

letter_digit(Letters, Letter, Digit) :-
    memberchk(Letter-Digit, Letters).

% Horner's rule: shift the number built so far one place and add the next digit.
digits_value([], Value, Value).
digits_value([Digit|Digits], Sofar, Value) :-
    Next #= Sofar * 10 + Digit,
    digits_value(Digits, Next, Value).
