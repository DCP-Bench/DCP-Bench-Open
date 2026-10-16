# Problem: Arrange the letters on the blocks so that every word can be spelled, each block carrying as many letters as it has sides.
from pycsp3 import *

num_blocks = data.num_blocks
num_sides = data.num_sides
alphabet = data.alphabet
# dice[i] is the block that carries letter alphabet[i]
dice = VarArray(size=data.num_letters, dom=range(num_blocks))
satisfy(
    # each block has one letter on each of its sides
    [Count(dice, value=b) == num_sides for b in range(num_blocks)],
    # the letters of each word lie on different blocks, so each block shows one letter at a time
    [AllDifferent([dice[alphabet.index(ch)] for ch in word]) for word in data.words_str],
)
