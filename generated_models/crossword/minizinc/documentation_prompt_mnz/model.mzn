include "globals.mzn";

% Given words sorted by length descending, then alphabetically:
% 0: HOSES (5)
% 1: LASER (5)
% 2: SHEET (5)
% 3: STEER (5)
% 4: SAILS (5)
% 5: KNOT (4)
% 6: KEEL (4)
% 7: HEEL (4)
% 8: HIKE (4)
% 9: LINE (4)
% 10: AFT (3)
% 11: ALE (3)
% 12: LEE (3)
% 13: EEL (3)
% 14: TIE (3)

% Words list for reference (not used directly in constraints)
% words = ["HOSES","LASER","SHEET","STEER","SAILS","KNOT","KEEL","HEEL","HIKE","LINE","AFT","ALE","LEE","EEL","TIE"];

% Number of words
int: n_words = 15;

% Lengths of words
array[0..n_words-1] of int: word_len = [5,5,5,5,5,4,4,4,4,4,3,3,3,3,3];

% The crossword grid (6 rows x 5 columns)
% '#' means black cell, '.' means white cell
% From the puzzle:
% Row 1: 1 . 2 . 3
% Row 2: # # . # .
% Row 3: # 4 . 5 .
% Row 4: 6 # 7 . .
% Row 5: 8 . . . .
% Row 6: . # # . #
%
% We will represent the grid as a 6x5 array of bool: true = white cell, false = black cell
array[1..6,1..5] of bool: white = [
  | true,  true,  true,  true,  true  | % row 1 (all white)
  | false, false, true,  false, true  | % row 2
  | false, true,  true,  true,  true  | % row 3
  | true,  false, true,  true,  true  | % row 4
  | true,  true,  true,  true,  true  | % row 5
  | true,  false, false, true,  false | % row 6
];

% The 8 words start at these positions (row, col) and directions:
% From the puzzle:
% 1: (1,1) horizontal length 3 (cells (1,1),(1,2),(1,3))? Actually puzzle shows 1 at (1,1) horizontal
% 2: (1,3) horizontal
% 3: (1,5) horizontal
% 4: (3,2) vertical
% 5: (3,4) vertical
% 6: (4,1) horizontal
% 7: (4,3) horizontal
% 8: (5,1) vertical

% Let's deduce lengths from the grid:
% 1: (1,1) horizontal: cells (1,1),(1,2),(1,3) => length 3
% 2: (1,3) horizontal: cells (1,3),(1,4),(1,5) => length 3
% 3: (1,5) vertical: cells (1,5),(2,5),(3,5),(4,5),(5,5) but (5,5) is white? (5,5) is true, (6,5) is false
% Actually (1,5) horizontal or vertical? Puzzle shows 3 at (1,5) horizontal? No, 3 is at (1,5) horizontal
% But (1,5) horizontal length? Only one cell? No, (1,5) is last column, so horizontal length 1 only
% So 3 must be vertical starting at (1,5)
% Let's check vertical length at (1,5): rows 1 to 5: (1,5),(2,5),(3,5),(4,5),(5,5) all white except (6,5) black
% So length 5 vertical for 3

% 4: (3,2) vertical: cells (3,2),(4,2),(5,2),(6,2) but (4,2) is black, so length 1 only? No, so 4 is vertical starting at (3,2) length 1? No
% Actually (3,2) is white, (4,2) black, so length 1 vertical
% But puzzle shows 4 at (3,2) vertical, so length 1? No, must be horizontal
% (3,2) horizontal: (3,2),(3,3),(3,4),(3,5) all white, length 4
% So 4 is horizontal length 4 at (3,2)

% 5: (3,4) vertical: (3,4),(4,4),(5,4),(6,4)
% (3,4) white, (4,4) white, (5,4) white, (6,4) white, length 4 vertical

% 6: (4,1) horizontal: (4,1),(4,2),(4,3),(4,4),(4,5)
% (4,1) white, (4,2) black, so length 1 only horizontal? No
% So 6 is vertical or horizontal?
% (4,1) vertical: (4,1),(5,1),(6,1)
% (4,1) white, (5,1) white, (6,1) white, length 3 vertical
% So 6 vertical length 3 at (4,1)

% 7: (4,3) horizontal: (4,3),(4,4),(4,5)
% all white, length 3 horizontal

% 8: (5,1) horizontal: (5,1),(5,2),(5,3),(5,4),(5,5)
% all white, length 5 horizontal

% Let's summarize the words with their start positions, directions and lengths:

% 1: (1,1) horizontal length 3
% 2: (1,3) horizontal length 3
% 3: (1,5) vertical length 5
% 4: (3,2) horizontal length 4
% 5: (3,4) vertical length 4
% 6: (4,1) vertical length 3
% 7: (4,3) horizontal length 3
% 8: (5,1) horizontal length 5

% We will define arrays for start positions, directions, and lengths
array[1..8] of int: start_row = [1,1,1,3,3,4,4,5];
array[1..8] of int: start_col = [1,3,5,2,4,1,3,1];
array[1..8] of int: length_word = [3,3,5,4,4,3,3,5];
array[1..8] of int: dir_row = [0,0,1,0,1,1,0,0]; % 0=horizontal, 1=vertical
array[1..8] of int: dir_col = [1,1,0,1,0,0,1,1];

% Decision variables: for each of the 8 words, select a word index from 0..14
array[1..8] of var 0..n_words-1: E;

% Constraint: word length must match the slot length
constraint
  forall(i in 1..8) (
    word_len[E[i]] == length_word[i]
  );

% Constraint: all selected words are different
constraint
  alldifferent(E);

% We need to ensure that crossing letters match
% For each pair of crossing cells, the letters must be equal
% We will model letters as integers 1..26 (A=1,...,Z=26)
% We will create a function to get letter at position in word

% Map words to letters (A=1,...,Z=26)
% words letters:
% HOSES: H O S E S
% LASER: L A S E R
% SHEET: S H E E T
% STEER: S T E E R
% SAILS: S A I L S
% KNOT: K N O T
% KEEL: K E E L
% HEEL: H E E L
% HIKE: H I K E
% LINE: L I N E
% AFT: A F T
% ALE: A L E
% LEE: L E E
% EEL: E E L
% TIE: T I E

% Let's define a 2D array letters[word_index, position] = letter code
array[0..n_words-1, 1..5] of int: letters = array2d(0..n_words-1, 1..5,
[
  % HOSES (5)
  ord('H')-ord('A')+1, ord('O')-ord('A')+1, ord('S')-ord('A')+1, ord('E')-ord('A')+1, ord('S')-ord('A')+1,
  % LASER (5)
  ord('L')-ord('A')+1, ord('A')-ord('A')+1, ord('S')-ord('A')+1, ord('E')-ord('A')+1, ord('R')-ord('A')+1,
  % SHEET (5)
  ord('S')-ord('A')+1, ord('H')-ord('A')+1, ord('E')-ord('A')+1, ord('E')-ord('A')+1, ord('T')-ord('A')+1,
  % STEER (5)
  ord('S')-ord('A')+1, ord('T')-ord('A')+1, ord('E')-ord('A')+1, ord('E')-ord('A')+1, ord('R')-ord('A')+1,
  % SAILS (5)
  ord('S')-ord('A')+1, ord('A')-ord('A')+1, ord('I')-ord('A')+1, ord('L')-ord('A')+1, ord('S')-ord('A')+1,
  % KNOT (4)
  ord('K')-ord('A')+1, ord('N')-ord('A')+1, ord('O')-ord('A')+1, ord('T')-ord('A')+1, 0,
  % KEEL (4)
  ord('K')-ord('A')+1, ord('E')-ord('A')+1, ord('E')-ord('A')+1, ord('L')-ord('A')+1, 0,
  % HEEL (4)
  ord('H')-ord('A')+1, ord('E')-ord('A')+1, ord('E')-ord('A')+1, ord('L')-ord('A')+1, 0,
  % HIKE (4)
  ord('H')-ord('A')+1, ord('I')-ord('A')+1, ord('K')-ord('A')+1, ord('E')-ord('A')+1, 0,
  % LINE (4)
  ord('L')-ord('A')+1, ord('I')-ord('A')+1, ord('N')-ord('A')+1, ord('E')-ord('A')+1, 0,
  % AFT (3)
  ord('A')-ord('A')+1, ord('F')-ord('A')+1, ord('T')-ord('A')+1, 0, 0,
  % ALE (3)
  ord('A')-ord('A')+1, ord('L')-ord('A')+1, ord('E')-ord('A')+1, 0, 0,
  % LEE (3)
  ord('L')-ord('A')+1, ord('E')-ord('A')+1, ord('E')-ord('A')+1, 0, 0,
  % EEL (3)
  ord('E')-ord('A')+1, ord('E')-ord('A')+1, ord('L')-ord('A')+1, 0, 0,
  % TIE (3)
  ord('T')-ord('A')+1, ord('I')-ord('A')+1, ord('E')-ord('A')+1, 0, 0
]);

% Function to get letter at position pos (1-based) in word w
function var int: letter_at(var int: w, int: pos) =
  letters[w,pos];

% We will create a map from grid cells to the word and position in that word
% For each cell, we find which words cover it and at which position

% Create arrays to store for each word the cells it covers