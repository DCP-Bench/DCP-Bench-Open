# Plan: allergy

Friends: Debra=0, Janet=1, Hugh=2, Rick=3. Foods: eggs, mold, nuts, ragweed. Surnames: baxter, lemon, malone, fleet.
Encoding: one-hot Bools X[food][p] (food goes to friend p) and Y[surname][p] (surname belongs to friend p); output = sum(p * bool).

- each food is allergy of exactly one friend -> sum_p X[f][p] == 1 per food; sum_f X[f][p] == 1 per friend
- each surname belongs to exactly one friend -> sum_p Y[s][p] == 1; sum_s Y[s][p] == 1 per friend
- Rick is not allergic to mold -> ~X[mold][3]
- Baxter is allergic to eggs -> Iff(Y[baxter][p], X[eggs][p]) for all p
- Hugh is neither surnamed Lemon nor Fleet -> ~Y[lemon][2], ~Y[fleet][2]
- Debra is allergic to ragweed -> X[ragweed][0]
- Janet (who isn't Lemon) is neither allergic to eggs nor to mold -> ~Y[lemon][1], ~X[eggs][1], ~X[mold][1]
- Objective: none (satisfaction); outputs eggs, mold, nuts, ragweed, baxter, lemon, malone, fleet as sum(p * bool).
