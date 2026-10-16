Problem: four friends (Debra=0, Janet=1, Hugh=2, Rick=3) each have a different surname (Baxter, Lemon, Malone, Fleet) and a different allergy (eggs, mold, nuts, ragweed); output the friend index for each surname and each allergy.
Each friend has one surname: all different over baxter, lemon, malone, fleet -> m.allDifferent(surnames, "AC")
Each friend has one allergy: all different over eggs, mold, nuts, ragweed -> m.allDifferent(allergies, "AC")
Baxter is allergic to eggs: same friend -> baxter.eq(eggs)
Rick is not allergic to mold: mold != 3 -> mold.ne(3)
Hugh is neither surnamed Lemon nor Fleet: lemon != 2, fleet != 2 -> lemon.ne(2), fleet.ne(2)
Debra is allergic to ragweed: ragweed = 0 -> ragweed.eq(0)
Janet (who isn't Lemon) is neither allergic to eggs nor to mold: lemon != 1 -> lemon.ne(1); eggs != 1, mold != 1
Objective: satisfaction (none)
