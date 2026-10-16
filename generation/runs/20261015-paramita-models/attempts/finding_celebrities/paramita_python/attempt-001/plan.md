# finding_celebrities plan (attempt-001)

- Given a list of people at a party and for each person the list of people they know -> one Bool c_i per person (celebrity), output celebrities = [c_0..c_4].
- A celebrity is a person that everybody at the party knows -> if some j does not know i (graph[j][i]=0, constant), then ~c_i; otherwise the condition is constant true.
- But only knows other celebrities -> if everybody knows i and i knows j != i (graph[i][j]=1), then c_i <-> AND of c_j over those j (Iff); if i knows nobody else, c_i is forced true.
- At least one celebrity is present -> Or(c_0..c_{n-1}).
- Satisfaction problem (no objective). Encoding: plain Bools, no integers.
