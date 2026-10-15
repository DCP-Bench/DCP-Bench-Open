A car of type t is at position p -> one-hot Bools x[p][t], sum over t == 1 per position; the sequence has sum(demand) positions
the sequence holds demand[t] cars of each type t -> per type t: sum over p of x[p][t] == demand[t]
option o: in any window of per_slots[o] consecutive positions, at most at_most[o] cars require it -> q[p][o] = sum over types t with requires[t][o] of x[p][t]; per option o and window start i: sum over p in window of q[p][o] <= at_most[o]
output sequence: seq[p] = sum over t of t * x[p][t] (car type number, from 0)
objective -> none (satisfaction)
