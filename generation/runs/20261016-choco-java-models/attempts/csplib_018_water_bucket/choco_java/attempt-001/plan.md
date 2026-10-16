Problem: water bucket. Three buckets with capacities 8, 5, 3 hold water; start 8,0,0; pour between buckets until 4,4,0.
Sequence state s[t] (t = 0..MAX_STEPS-1), 3 amounts each, bounded by capacity; PAD (-1) after the goal.
s[0] = initial state -> arithm "=" per bucket.
Each step is a legal pour (or padding) -> table over (s[t], s[t+1]): legal pour pairs, (goal, PAD), (PAD, PAD).
Goal is reached and then only padding follows: the table allows PAD only after goal.
Last state is goal or PAD -> table over the last state.
Cost = number of transfers = count of real states after the first -> sum of reified "bucket 0 not PAD" booleans for t >= 1.
Objective: minimize cost; output cost and sequence.
