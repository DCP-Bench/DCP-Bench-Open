Problem: four friends (Debra=0, Janet=1, Hugh=2, Rick=3) each have a surname (Baxter, Lemon, Malone, Fleet) and a different allergy (eggs, mold, nuts, ragweed). Each output is the friend index holding that food or surname.
Four friends each have a different food: all different on eggs, mold, nuts, ragweed -> distinct(*this, foods, IPL_DOM)
Four friends each have a different surname: all different on baxter, lemon, malone, fleet -> distinct(*this, surnames, IPL_DOM)
Rick is not allergic to mold -> rel(*this, mold, IRT_NQ, 3)
Baxter is allergic to eggs (same friend) -> rel(*this, baxter, IRT_EQ, eggs)
Hugh is neither surnamed Lemon nor Fleet -> rel(*this, lemon, IRT_NQ, 2); rel(*this, fleet, IRT_NQ, 2)
Debra is allergic to ragweed -> rel(*this, ragweed, IRT_EQ, 0)
Janet (who isn't Lemon) is neither allergic to eggs nor mold -> rel(*this, lemon, IRT_NQ, 1); rel(*this, eggs, IRT_NQ, 1); rel(*this, mold, IRT_NQ, 1)
Branching: all eight variables, INT_VAR_SIZE_MIN, INT_VAL_MIN (satisfaction, no objective).
Objective: none (satisfaction).
