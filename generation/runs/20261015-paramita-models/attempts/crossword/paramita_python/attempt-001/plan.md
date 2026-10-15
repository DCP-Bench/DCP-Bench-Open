# crossword plan

Complete the 6x5 grid: eight slots (four across, four down) numbered 1..8; each slot takes one word from the list of 15, lengths must match.
-> one-hot Bool w[k][j] per slot k and word j; sum_j w[k][j] == 1; words with the wrong length are forbidden (~w[k][j]).

Select 8 words from the list of 15, one per slot, each word used at most once.
-> sum_k w[k][j] <= 1 per word j.

Crossing letters must agree at every shared cell.
-> for each shared cell (slot a at index i, slot b at index j) and each pair of words u, v with different letters at those positions: ~(w[a][u] & w[b][v]).

Print the selected words E (word index per numbered location 1..8, starting from 0).
-> E[k] = sum_j j * w[k][j] (word index per slot, in order of the numbers).

Word order: sorted by length descending, then alphabetically (HOSES 0 ... TIE 14).
Objective: none (satisfaction).
