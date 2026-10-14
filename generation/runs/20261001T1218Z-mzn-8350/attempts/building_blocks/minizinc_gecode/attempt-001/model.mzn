% Building blocks: each alphabet block carries one letter on each of its sides.
% Place every letter of the alphabet on a block so that every given word can be
% spelled by taking its letters from different blocks.
include "globals.mzn";

int: num_blocks;
int: num_sides;                    % letters on each block
int: num_letters;                  % number of letters in the alphabet
string: alphabet;                  % the letters, one character each
array[int] of string: words_str;   % the words that have to be spelled

% the alphabet as an array of one-character strings (MiniZinc 2.9.3: string_split
% with an empty separator returns the characters of the string)
array[int] of string: letters = string_split(alphabet, "");

% position of a character in the alphabet, which is the letter's number
function int: letter_number(string: c) = min([i | i in index_set(letters) where letters[i] = c]);

% dice[l] = the block on which letter l is placed (blocks are numbered from 1
% here and from 0 in the printed output)
array[1..num_letters] of var 1..num_blocks: dice;

% the letters of a word must be on different blocks
constraint forall(w in index_set(words_str))
    (alldifferent([dice[letter_number(c)] | c in string_split(words_str[w], "")]));

% there must be exactly num_sides letters on each block
constraint global_cardinality(dice, [b | b in 1..num_blocks], [num_sides | b in 1..num_blocks]);

solve satisfy;

output ["{\"dice\": [", join(", ", [show(fix(dice[l]) - 1) | l in 1..num_letters]), "]}"];
