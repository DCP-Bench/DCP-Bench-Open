:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% General store (cryptarithm): each letter stands for a different digit. Sixteen
% words, read as numbers, add up to ALLWOOL. Find the digit of every letter.
% The problem has no instance data; the words below are the sign in the
% statement. As in the reference, a word may start with the digit 0.
%
% The addition is posted column by column, the way it is done on paper: in each
% column the digits of the words plus the carry from the column to the right
% equal the digit of ALLWOOL plus 10 times the carry into the next column. This
% form is used because stating the sum over whole word values did not finish
% within the 180 s execution limit.
model(_Instance, Vars, ['A'-A, 'B'-B, 'C'-C, 'E'-E, 'H'-H, 'L'-L, 'O'-O, 'P'-P, 'S'-S, 'W'-W]) :-
    Letters = ['C'-C, 'H'-H, 'E'-E, 'S'-S, 'A'-A, 'B'-B, 'O'-O, 'W'-W, 'P'-P, 'L'-L],
    pairs_values(Letters, Vars),

    % each letter is a digit, and different letters are different digits
    Vars ins 0..9,
    all_distinct(Vars),

    % the words above the line, and the total below it
    Words = ['CHESS', 'CASH', 'BOWWOW', 'CHOPS', 'ALSOPS', 'PALEALE', 'COOL',
             'BASS', 'HOPS', 'ALES', 'HOES', 'APPLES', 'COWS', 'CHEESE',
             'CHSOAP', 'SHEEP'],
    Total = 'ALLWOOL',
    maplist(word_digits(Letters), Words, WordsDigits),
    word_digits(Letters, Total, TotalDigits),

    % A carry is at most the number of words: if the carry in is at most n, a
    % column of n digits adds up to at most 9n + n, so the carry out is at most n.
    length(Words, MaxCarry),

    % add the columns from the units to the left; nothing is carried out of the
    % last column
    add_columns(WordsDigits, TotalDigits, 0, MaxCarry).

% word_digits(+Letters, +Word, -Digits): the digit variables of Word, with the
% units digit first.
word_digits(Letters, Word, Digits) :-
    atom_chars(Word, Chars),
    reverse(Chars, UnitsFirst),
    maplist(letter_digit(Letters), UnitsFirst, Digits).

letter_digit(Letters, Letter, Digit) :-
    memberchk(Letter-Digit, Letters).

% add_columns(+WordsDigits, +TotalDigits, +CarryIn, +MaxCarry): the remaining
% columns of the addition hold. The digit lists of the words have the columns
% already done removed; a word that has run out of digits no longer takes part,
% and the total contributes 0 once its own digits have run out.
add_columns(WordsDigits, TotalDigits, CarryIn, MaxCarry) :-
    (   WordsDigits == [], TotalDigits == []
    ->  true
    ;   column(WordsDigits, ColumnDigits, WordsDigitsRest),
        (   TotalDigits = [TotalDigit|TotalDigitsRest]
        ->  true
        ;   TotalDigit = 0, TotalDigitsRest = []
        ),
        sum(ColumnDigits, #=, ColumnSum),
        CarryOut in 0..MaxCarry,
        ColumnSum + CarryIn #= TotalDigit + 10 * CarryOut,
        (   WordsDigitsRest == [], TotalDigitsRest == []
        ->  CarryOut #= 0
        ;   add_columns(WordsDigitsRest, TotalDigitsRest, CarryOut, MaxCarry)
        )
    ).

% column(+WordsDigits, -ColumnDigits, -Rest): the lowest digit of every word,
% and the words that still have digits after that.
column([], [], []).
column([[D|Ds]|Words], [D|Digits], Rest) :-
    column(Words, Digits, RestOfWords),
    (   Ds == []
    ->  Rest = RestOfWords
    ;   Rest = [Ds|RestOfWords]
    ).
