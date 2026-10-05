% Building blocks: each of num_blocks alphabet blocks has one letter on each of its
% num_sides sides. Place the letters on the blocks so that every word in the list can be
% spelt, which needs the letters of a word to be on different blocks.
% Output dice(L, B): letter number L (its position in alphabet, from 0) is on block B.

% Letter numbers 0..num_letters-1 and block numbers 0..num_blocks-1, from the instance.
letter(0..N-1) :- num_letters(N).
block(0..B-1) :- num_blocks(B).

% letter_code(L, C): letter number L is the character C, the L-th character of alphabet.
letter_code(L,C) :- alphabet_char(L,C).

% word_letter(W, P, L): the P-th character of word W is letter number L.
word_letter(W,P,L) :- words_str_char(W,P,C), letter_code(L,C).

% Each letter is on exactly one block.
1 { dice(L,B) : block(B) } 1 :- letter(L).

% The letters in a word must be on different blocks.
:- word_letter(W,P1,L1), word_letter(W,P2,L2), P1 < P2, dice(L1,B), dice(L2,B).

% Every block carries exactly num_sides letters.
:- block(B), num_sides(S), #count { L : dice(L,B) } != S.

#show dice/2.
