Boolean matrix M[i][c] with m.sum "=" 1 per ball and m.sum "<=" 2 per triple and box is fast on these sizes; no global fits the triple constraint.
Ball output as IntVar via m.scalar(M[i], weights, "=", balls[i]) gives the 1-based box directly.
