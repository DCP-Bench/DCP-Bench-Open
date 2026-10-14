% Crossword: pick 8 different words from a list of 15 to fill the 8 numbered
% slots of a small crossword grid so that every place where two slots cross
% holds the same letter in both words.
include "globals.mzn";

% The puzzle itself is fixed by the problem, so its data is mirrored here.
int: n_words = 15;
int: word_len = 5;
int: n_slots = 8;

% The words as letter numbers (a=1 .. z=26), padded with 0 to length 5, sorted
% longest first and then alphabetically: HOSES LASER SAILS SHEET STEER HEEL HIKE
% KEEL KNOT LINE AFT ALE EEL LEE TIE.
array[1..n_words, 1..word_len] of int: letters = array2d(1..n_words, 1..word_len, [
    8, 15, 19, 5, 19,   12, 1, 19, 5, 18,   19, 1, 9, 12, 19,   19, 8, 5, 5, 20,   19, 20, 5, 5, 18,
    8, 5, 5, 12, 0,     8, 9, 11, 5, 0,     11, 5, 5, 12, 0,    11, 14, 15, 20, 0,  12, 9, 14, 5, 0,
    1, 6, 20, 0, 0,     1, 12, 5, 0, 0,     5, 5, 12, 0, 0,     12, 5, 5, 0, 0,     20, 9, 5, 0, 0]);

% each crossing is [slot a, letter position in a, slot b, letter position in b], slots
% and positions counted from 1
array[1..12, 1..4] of int: crossings = array2d(1..12, 1..4, [
    1, 3, 2, 1,   1, 5, 3, 1,   4, 2, 2, 3,   4, 3, 5, 1,   4, 4, 3, 3,   7, 1, 2, 4,
    7, 2, 5, 2,   7, 3, 3, 4,   8, 1, 6, 2,   8, 3, 2, 5,   8, 4, 5, 3,   8, 5, 3, 5]);

% E[s] = the word placed in slot s, numbered from 0 as in the answer (word w is
% row w + 1 of the letter table); all slots get different words
array[1..n_slots] of var 0..n_words - 1: E;
constraint all_different(E);

% where two slots cross, the two words show the same letter
constraint forall(k in 1..12) (
    letters[E[crossings[k, 1]] + 1, crossings[k, 2]] = letters[E[crossings[k, 3]] + 1, crossings[k, 4]]);

solve satisfy;

output ["{\"E\": [", join(", ", [show(E[s]) | s in 1..n_slots]), "]}"];
