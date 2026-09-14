# csplib_033_word_design

num_words DNA words of length n over {A,C,G,T} = {1,2,3,4} such that each word
has four symbols from {C,G}, each pair of distinct words differs in at least
four positions, and for every ordered pair x, y (x = y included) the reverse of
x and the Watson-Crick complement of y differ in at least four positions.

- Instance inputs: `n`, `num_words`. Output: `words` — num_words rows of n
  integers in 1..4.
- Satisfaction. The complement of a letter is 5 minus the letter.
