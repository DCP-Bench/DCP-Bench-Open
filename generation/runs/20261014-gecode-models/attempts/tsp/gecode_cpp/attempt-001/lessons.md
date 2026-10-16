circuit(*this, cost, succ, total) with an n*n IntArgs cost matrix gave the optimum on all five instances (up to 30 cities) with the default branching: INT_VAR_SIZE_MIN on succ.
The 30-city instance took 115 s of 180 s, so a stronger tour bound would help larger instances; not needed here.
The cost matrix is built from the locations in C++ with std::lround, matching the description's rounding.
