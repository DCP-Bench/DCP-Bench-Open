Hilary and Jocelyn are married; they invite num_couples couples who are friends -> persons 0,1 are the host couple (Hilary, Jocelyn), persons 2k,2k+1 are invited couples; N = 2*(num_couples+1); spouse(i) = i xor 1
they shake hands with each other -> one BoolVar per unordered pair {i,j}, shake(i,j) = shake(j,i)
Nobody shakes hands with him or herself -> no variable for i = j (degree sums skip i)
or with his or her spouse -> no variable for j = spouse(i) (no variable created; degree sums skip the spouse)
After there has been some handshaking, Jocelyn asks how many hands each person has shaken -> hands[i] = m.sum over shake(i,j) for j not i and not spouse(i)
All the answers are different -> m.allDifferent over hands[i] for all i except Jocelyn (index 1), "AC"
implied (pigeonhole, not an answer): the answers are n-1 distinct values in 0..n-2, so they sum to (n-2)(n-1)/2 -> m.sum(answers, "=", ...)
symmetry (interchangeable couples and spouses): order hands by couple -> arithm "<" within each couple and between first members of consecutive invited couples
Print the number of hands Hilary has shaken (hil) -> out hil = hands[0]
objective: satisfaction (none)
search: domOverWDeg on the handshake variables with Luby restarts (attempt 001 without it timed out on the second solution)
