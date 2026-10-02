% Building blocks: alphabet blocks carry one letter on each side; arrange the letters on the
% blocks so that every word in a given list can be spelt, which needs the letters of a word to
% sit on different blocks, and every block carries exactly num_sides letters.
% Instance facts: num_blocks(B), num_sides(S), num_letters(N); alphabet(A): the letters, as a
% string, so that letter number L is the L-th character of A; words_str(W, S): word number W as
% a string. Pure ASP cannot take a string apart, so two small Lua functions read characters.
#script (lua)
function string_length(s)
  return #s
end

-- zero-based number of the character at zero-based position p of the word s in the alphabet
function letter_number(s, p, alphabet)
  local c = string.sub(s, p + 1, p + 1)
  return string.find(alphabet, c, 1, true) - 1
end
#end.

letter(0..N-1) :- num_letters(N).
block(0..B-1) :- num_blocks(B).

% dice(L, B): letter L is placed on block B. Each letter is on exactly one block.
1 { dice(L,B) : block(B) } 1 :- letter(L).

% There must be exactly num_sides letters on each block.
:- block(B), num_sides(S), S != #count { L : dice(L,B) }.

% word_letter(W, P, L): the P-th letter of word W (from 0) is the letter number L.
word_letter(W,P,@letter_number(S,P,A)) :- words_str(W,S), alphabet(A), P = 0..@string_length(S) - 1.

% The letters of a word must be on different blocks.
:- word_letter(W,P1,L1), word_letter(W,P2,L2), P1 < P2, dice(L1,B), dice(L2,B).

#show dice/2.
