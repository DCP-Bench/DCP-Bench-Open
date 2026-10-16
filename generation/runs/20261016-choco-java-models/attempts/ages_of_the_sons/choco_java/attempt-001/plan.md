# Plan: ages_of_the_sons (A1, A2, A3 = ages, oldest first)

- "The product of their ages is 36." -> age[0]*age[1]*age[2] = 36 (`mul` expression, `eq(36).post()`)
- Ages are positive whole numbers; ages are bounded by 36 since each factor divides 36 -> domains 1..36
- "Print the ages starting from the oldest." -> age[0] >= age[1] >= age[2] (`ge().post()`)
- "The sum of their ages equals the number of windows" (unknown W) -> sum = age[0]+age[1]+age[2] (`m.sum`)
- "I need more information" (after the product) -> constant fact: 36 alone gives sums 38,21,16,14,13,11,10; not a separate constraint
- "I need more information" (after the sum) -> at least two candidate triples with product 36 have the same sum as the answer:
  b_j = [sum = s_j] over the 8 candidates, `m.sum(b, ">=", 2)`
- "The oldest son has blue eyes. I got it." -> among candidates with product 36 and the same sum, only one has a unique oldest son:
  for each candidate j with c_j1 > c_j2: sum = s_j implies age = c_j (`m.ifThen`)
- The answer needs a unique oldest son: age[0] > age[1] (`gt().post()`)
- Objective: none (satisfaction)
