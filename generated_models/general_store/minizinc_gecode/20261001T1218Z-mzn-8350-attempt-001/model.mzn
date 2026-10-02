% General store: a cryptarithm. Each different letter stands for a different
% digit; the sixteen words above the line, read as numbers, add up to the number
% ALLWOOL. Find the digit of every letter. This problem has no instance data: the
% words are part of the problem statement.
include "globals.mzn";

% the ten letters, in the order of the answer (C, H, E, S, A, B, O, W, P, L)
array[1..10] of string: letter = ["C", "H", "E", "S", "A", "B", "O", "W", "P", "L"];

% digit[i] = the digit that letter i stands for
array[1..10] of var 0..9: digit;

% different letters stand for different digits
constraint all_different(digit);

% the digit of a letter, looked up by its name
function var int: digit_of(string: c) = digit[min([i | i in 1..10 where letter[i] = c])];

% the number a word stands for: its letters are its decimal digits
function var int: number(string: word) =
    let { array[int] of string: chars = string_split(word, "") }
    in sum(i in index_set(chars)) (pow(10, length(chars) - i) * digit_of(chars[i]));

% the words that are added up (above the line)
array[1..16] of string: addends = [
    "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
    "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"];

% the words above the line add up to ALLWOOL
constraint sum(w in 1..16) (number(addends[w])) = number("ALLWOOL");

solve satisfy;

output ["{\"C\": ", show(digit[1]), ", \"H\": ", show(digit[2]), ", \"E\": ", show(digit[3]),
        ", \"S\": ", show(digit[4]), ", \"A\": ", show(digit[5]), ", \"B\": ", show(digit[6]),
        ", \"O\": ", show(digit[7]), ", \"W\": ", show(digit[8]), ", \"P\": ", show(digit[9]),
        ", \"L\": ", show(digit[10]), "}"];
