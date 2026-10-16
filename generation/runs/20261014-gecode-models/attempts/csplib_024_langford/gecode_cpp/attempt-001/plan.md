Langford: two sets of the numbers 1 to k; arrange the 2k numbers in one sequence.
-> class Langford, reads k; pos[2(i-1)], pos[2(i-1)+1] are the two positions of value i.

the 2k numbers are arranged into a single sequence
-> the 2k positions are all different, a permutation of 0..2k-1 -> distinct(*this, pos, IPL_DOM) (domain-consistent permutation).

the two i's appear i+1 numbers apart
-> rel(*this, pos[2j+1] == pos[2j] + j + 2) for value i = j+1 (second position minus first is i+1); linear, no global fits.

the sequence holds the value i at the two positions of i
-> element(*this, sol, pos[2j], i) for both positions of value i (element over variables is domain consistent); this also makes every value appear exactly twice.

branching (every decision is a position pair; sol is then fixed by the element posts)
-> branch(*this, pos, INT_VAR_SIZE_MIN(), INT_VAL_MIN()); branch(*this, sol, INT_VAR_NONE(), INT_VAL_MIN()) as a safety net.

satisfaction: no objective; the output is the sequence sol.
