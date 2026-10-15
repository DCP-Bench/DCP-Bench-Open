# Plan: five floors (Baker, Cooper, Fletcher, Miller, Smith on floors 1..5)
- They all live on different floors -> one-hot per person, exactly one floor each, at most one person per floor -> ==1 per floor
- Baker does not live on the fifth floor -> ~B[5]
- Cooper does not live on the first floor -> ~C[1]
- Fletcher does not live on either the fifth or the first floor -> ~F[5], ~F[1]
- Miller lives on a higher floor than Cooper -> integer M > C (integer expressions over one-hot)
- Smith does not live on a floor adjacent to Fletcher -> for each pair of adjacent floors, ~(S[v] & F[v+-1])
- Fletcher does not live on a floor adjacent to Cooper's -> for each pair of adjacent floors, ~(F[v] & C[v+-1])
- Objective: none (satisfaction). Outputs B, C, F, M, S as integer expressions.
