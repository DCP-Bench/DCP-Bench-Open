There are 13 people. 4 of them are male. -> 13 positions, 4 males (0), 9 females (1): sum(b) = 9 (m.sum(b, "=", 9)), or equivalently the male count is 4
They randomly enter a room one at a time. -> the sequence order is the decision: b[0..12] in position order
the males and females enter so that the ratio of females to males in the room at any one time is no greater than 7/3 -> for every prefix k: 3 * F_k <= 7 * M_k with F_k = females among the first k+1, M_k = (k+1) - F_k; posted as 10 * F_k <= 7 * (k+1) (same inequality), F_k a prefix sum
Print the sequence of people entering the room (sequence), 0 = male, 1 = female -> output sequence = BoolVar[13]
objective: none (satisfaction)
