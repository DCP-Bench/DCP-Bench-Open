Problem: six suspects, who is guilty; innocent suspects tell the truth, guilty ones lie.

- The getaway car holds two, so at most two guilty -> sum(guilty) <= 2
- Each suspect's statement is true exactly when the suspect is innocent -> truth_X != guilty_X
- Artie: "It wasn't me." -> truth = not artie
- Bill: "Crackitt was in it up to his neck." -> truth = crackitt
- Crackitt: "No I wasn't." -> truth = not crackitt
- Dodgy: "If Crackitt did it, Bill did it with him." -> truth = crackitt => bill (reified)
- Edgy: "Nobody did it alone." -> truth = (number guilty != 1) (reified sum)
- Fingers: "Artie and Dodgy together." -> truth = artie and dodgy (reified)
- Objective: none (satisfaction); outputs artie, bill, crackitt, dodgy, edgy, fingers as BoolVars.
