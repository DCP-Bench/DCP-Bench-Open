Rounded Euclidean distance is the bottleneck for tsp, not the tour encoding (Boolean successor, exactly-one, MTZ): with the squared distance as cost, the 12-city example optimum is proven in 7.5 s.
The rounded form, dist = sum over candidates k of k when k*k-k+1 =< d2 =< k*k+k, does not prove the 12-city optimum within 180 s, nor does the bounded Int with nonlinear constraints.
Helper symbols defined by equations (sqd, lo, hi) stay symbolic in z3; inlining the coordinate arithmetic in the guard did not fix the rounded version.
Accepted only on the 6-city duplicate_and_collinear instance (1 of 5), so this attempt is not retained.
