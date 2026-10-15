# Plan: wolf, goat and cabbage (stages from instance["stage"], states 0..stage-1)
- "all four start on the starting shore" -> ~Bool at stage 0 for wolf, goat, cabbage, boat -> Bool literals (negated)
- "all four end on the destination shore" -> Bool at last stage -> Bool literals
- "the farmer crosses the river at every stage" (boat alternates) -> Iff(boat_t, ~boat_t+1)
- "the boat can carry only the farmer and a single item" -> per stage, per item a moves Bool with Iff(moves, a + b == 1); sum(moves) <= 1
- "an item crosses only with the farmer from the same shore" -> If(moves, Iff(item_t, boat_t))
- "if left unattended the wolf would eat the goat" -> If(Iff(wolf_t, goat_t), Iff(boat_t, goat_t))
- "the goat would eat the cabbage" -> If(Iff(goat_t, cabbage_t), Iff(boat_t, goat_t))
- objective: none (satisfaction); outputs are the Bool lists per stage -> JSON booleans
