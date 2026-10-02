:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Building blocks: alphabet blocks carry one letter on each side and together
% hold every letter of the alphabet once. Decide which letters go on which
% block so that every word in the list can be spelled by putting its letters on
% different blocks.
model(Instance, Vars, [dice-Dice]) :-
    NumBlocks = Instance.num_blocks,
    NumSides = Instance.num_sides,       % letters on each block
    NumLetters = Instance.num_letters,
    Alphabet = Instance.alphabet,        % the letters, one atom; position = letter number
    Words = Instance.words_str,          % the words to spell, as atoms

    % Dice[l] = the block (numbered from 0) that letter number l is on
    Top is NumBlocks - 1,
    length(Dice, NumLetters),
    Dice ins 0..Top,

    % the letters of a word are on different blocks
    atom_chars(Alphabet, Letters),
    maplist(letters_on_different_blocks(Letters, Dice), Words),

    % each block carries exactly num_sides letters
    numlist(0, Top, Blocks),
    pairs_keys_values(Counts, Blocks, Sides),
    length(Sides, NumBlocks),
    maplist(=(NumSides), Sides),
    global_cardinality(Dice, Counts),
    Vars = Dice.

% The blocks holding the letters of Word are pairwise different.
letters_on_different_blocks(Letters, Dice, Word) :-
    atom_chars(Word, WordLetters),
    maplist({Letters, Dice}/[Letter, Block]>>(nth0(Index, Letters, Letter), nth0(Index, Dice, Block)),
            WordLetters, Blocks),
    all_distinct(Blocks).
