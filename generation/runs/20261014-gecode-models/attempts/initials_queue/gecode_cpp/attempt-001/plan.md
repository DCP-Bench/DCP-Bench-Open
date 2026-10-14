Problem: ten people in a queue, each with initials that are an alphabetically ordered pair of distinct letters from A..E; every person's pair is different; no two neighbours share a letter; front person BE, second CD, last BD. Output the queue front to back as [10][2] letters 0..4.

Each pair uses a[i] < b[i] over 0..4 -> rel(a[i] < b[i]) with a, b in 0..4 (the alphabetical order is part of the requirement).
Each pair is distinct from the others -> pair code c[i] = 5*a[i] + b[i] (unique decoding of a < b), distinct(*this, c, IPL_DOM).
No-one repeats a letter of the person in front (neighbours share no letter) -> four rel(a[i] != a[i+1]), rel(a[i] != b[i+1]), rel(b[i] != a[i+1]), rel(b[i] != b[i+1]) for each i in 0..8. No map row fits "no shared letter between neighbours" beyond the pairwise `!=`, which is the natural encoding over IntVar letters; keep it as plain NQ relations.
Front person BE -> a[0] = 1, b[0] = 4 (fixed from the description).
Second person CD -> a[1] = 2, b[1] = 3 (fixed from the description).
Last person BD -> a[9] = 1, b[9] = 3 (fixed from the description).
Branching -> branch on a then b with INT_VAR_SIZE_MIN, INT_VAL_MIN (all decision letters are fixed by the search).
Objective -> none (satisfaction). Output "queue" as std::vector<IntVarArgs>, one pair per person.
