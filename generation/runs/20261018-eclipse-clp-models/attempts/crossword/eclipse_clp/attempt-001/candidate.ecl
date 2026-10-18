% Crossword puzzle.
%
% We are to complete the puzzle. The grid is 6 rows by 5 columns; '#' cells are blocks.
% The numbers 1..8 in the grid correspond to the words that start at those locations.
% Slots: 1 across (5), 2 down (5), 3 down (5), 4 across (4), 5 down (4), 6 down (3),
% 7 across (3), 8 across (5).
%
% Words are given sorted by length (longest first), then alphabetically, so word 0
% is HOSES and word 14 is TIE.

:- lib(ic).
:- lib(listut).

word_list(["HOSES", "LASER", "SAILS", "SHEET", "STEER",
           "HEEL", "HIKE", "KEEL", "KNOT", "LINE",
           "AFT", "ALE", "EEL", "LEE", "TIE"]).

% The eight slots, each as its cells in reading order (Row-Col).
slot_cells([
    [1-1, 1-2, 1-3, 1-4, 1-5],      % 1 across
    [1-3, 2-3, 3-3, 4-3, 5-3],      % 2 down
    [1-5, 2-5, 3-5, 4-5, 5-5],      % 3 down
    [3-2, 3-3, 3-4, 3-5],           % 4 across
    [3-4, 4-4, 5-4, 6-4],           % 5 down
    [4-1, 5-1, 6-1],                % 6 down
    [4-3, 4-4, 4-5],                % 7 across
    [5-1, 5-2, 5-3, 5-4, 5-5]       % 8 across
]).

% The white cells of the grid, one letter variable each.
open_cells([1-1, 1-2, 1-3, 1-4, 1-5,
            2-3, 2-5,
            3-2, 3-3, 3-4, 3-5,
            4-1, 4-3, 4-4, 4-5,
            5-1, 5-2, 5-3, 5-4, 5-5,
            6-1, 6-4]).

model(_Instance, Vars, ['E'-Ss]) :-
    word_list(Words),
    ( foreach(W, Words), foreach(C, WordCodes) do string_list(W, C) ),
    ( foreach(C, WordCodes), foreach(L, WordLens) do length(C, L) ),

    slot_cells(Slots),
    length(Slots, NS),
    length(Ss, NS),
    open_cells(Cells),
    length(Cells, NC),
    length(Letters, NC),
    Letters :: 65..90,

    % We need to select 8 words from the list of 15 words, such that the above
    % crossword puzzle can be completed. Each slot takes one word of its length,
    % the selected words are distinct, and crossing cells carry the same letter.
    post_slots(Slots, Ss, Letters, Cells, WordCodes, WordLens),
    alldifferent(Ss),

    % Print the selected words (E) as a list of 8 integers, one per numbered slot.
    append(Ss, Letters, Vars).

% Each slot takes a word of its length; a word that is chosen fixes its letters
% at the slot's cells.
post_slots([], [], _, _, _, _).
post_slots([SC|SCs], [S|Ss], Letters, Cells, WordCodes, WordLens) :-
    length(SC, Len),
    word_indices_of_len(WordLens, Len, 0, Idx),
    S :: Idx,
    post_slot_words(Idx, S, SC, Letters, Cells, WordCodes),
    post_slots(SCs, Ss, Letters, Cells, WordCodes, WordLens).

post_slot_words([], _, _, _, _, _).
post_slot_words([W|Ws], S, SC, Letters, Cells, WordCodes) :-
    nth0(W, WordCodes, Codes),
    post_letters(SC, Codes, S, W, Letters, Cells),
    post_slot_words(Ws, S, SC, Letters, Cells, WordCodes).

post_letters([], [], _, _, _, _).
post_letters([C|Cs], [Code|Codes], S, W, Letters, Cells) :-
    cell_var(C, Cells, Letters, V),
    (S #= W) => (V #= Code),
    post_letters(Cs, Codes, S, W, Letters, Cells).

cell_var(C, [C|_], [V|_], V) :- !.
cell_var(C, [_|Cs], [_|Vs], V) :- cell_var(C, Cs, Vs, V).

% Indices (from I onward) of the words whose length is Len.
word_indices_of_len([], _, _, []).
word_indices_of_len([L|Ls], Len, I, Idx) :-
    I1 is I + 1,
    (   L =:= Len
    ->  Idx = [I|Rest]
    ;   Idx = Rest
    ),
    word_indices_of_len(Ls, Len, I1, Rest).

