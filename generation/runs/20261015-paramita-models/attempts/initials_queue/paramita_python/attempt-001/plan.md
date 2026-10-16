# initials_queue plan

Letters A..E are 0..4. The 10 possible initials are the alphabetically ordered pairs (a < b), indexed PAIRS[j].

- "Each of them had initials which were an alphabetically ordered pair of distinct letters from the first five letters" -> one-hot p[i][j] per queue place i, sum over j == 1
- "None of the people had the same initials as any other" (10 people, 10 pairs) -> each pair used exactly once: sum over i of p[i][j] == 1
- "no-one shared a letter with the person in front of them" -> for adjacent places i, i+1 and pairs that share a letter: ~(p[i][j] & p[i+1][l])
- "BE was at the front of the queue" -> p[0][BE]
- "with CD right behind" -> p[1][CD]
- "BD was right at the end of the queue" -> p[9][BD]
- Output queue[i] = [first letter, second letter] as integer expressions: sum(a * p[i][j]) and sum(b * p[i][j])
- Objective: none (satisfaction).
