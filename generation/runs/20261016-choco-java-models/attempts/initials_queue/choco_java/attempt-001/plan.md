Each of them had initials which were an alphabetically ordered pair of distinct letters from A,B,C,D,E -> queue[i][0] < queue[i][1], both in 0..4 (letters 0..4)
None of the people had the same initials as any other -> allDifferent over code[i] = 5*first + second (m.allDifferent "AC")
no-one shared a letter with the person in front of them -> for consecutive i: queue[i][a] != queue[i+1][b] for all a, b (arithm "!=")
Mathematician BE was at the front of the queue -> queue[0] = (1, 4) (m.arithm "=")
with CD right behind -> queue[1] = (2, 3)
BD was right at the end of the queue -> queue[9] = (1, 3)
Print the queue of the initials as 10 lists of 2 integers from 0 to 4 -> output queue[10][2]
Objective: none (satisfaction)
