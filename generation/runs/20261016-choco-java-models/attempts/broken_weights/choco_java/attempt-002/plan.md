# broken_weights plan (attempt-001)

Variables: weights[i] in 1..M for the n pieces, M and n from the instance.
- "the weight of each piece was a whole number of pounds" -> weights are IntVars with bounds 1..M
- "the pieces together make the total weight M" -> sum(weights) = M -> m.sum
- "the pieces are all different" (reference rule, per instance notes) -> allDifferent
- "every integral weight between 1 and the total can be weighed" -> for each t in 1..M, a vector of coefficients in {-1, 0, 1} (a piece on the same side as the object, the other side, or off the scale) with scalar(coefficients, weights) = t. Coefficient vectors are one IntVar[n] per t.
- Objective: none (satisfaction). Output: weights.
