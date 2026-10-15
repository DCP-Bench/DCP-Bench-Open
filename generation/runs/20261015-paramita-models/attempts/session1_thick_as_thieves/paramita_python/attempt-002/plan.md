# Plan: session1_thick_as_thieves

Bool per suspect: guilty_<name> (true = did the robbery). Six suspects, no instance data.

- "the getaway car had been barely big enough to hold two" -> sum(guilty) <= 2
- "at least four of them were innocent" -> sum(guilty) <= 2 (same bound)
- "the guilty one or ones" -> sum(guilty) >= 1
- "the innocent ones would tell the truth, while the guilty one or ones would lie" -> per suspect: Iff(~guilty_s, statement_s)
- ARTIE: "It wasn't me." -> statement ~guilty_artie
- BILL: "Crackitt was in it up to his neck." -> statement guilty_crackitt
- CRACKITT: "No I wasn't." -> statement ~guilty_crackitt
- DODGY: "If Crackitt did it, Bill did it with him." -> statement If(guilty_crackitt, guilty_bill)
- EDGY: "Nobody did it alone." -> statement Or(sum(guilty) >= 2, sum(guilty) == 0)
- FINGERS: "it was Artie and Dodgy together." -> statement guilty_artie & guilty_dodgy & (sum(guilty) == 2)
- Objective: none (satisfaction); outputs = guilty_<name> per suspect.
