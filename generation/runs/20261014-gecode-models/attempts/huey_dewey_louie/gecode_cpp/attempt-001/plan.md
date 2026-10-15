Cub scouts cannot lie, so every statement made is true. Each guilty flag is a Boolean (1 = guilty).
Huey: "Dewey and Louie have equal share in it; if one is guilty, so is the other." -> dewey == louie (Huey's statement holds, so the equality holds): rel(*this, dewey, IRT_EQ, louie)
Dewey: "If Huey is guilty, then so am I." -> huey -> dewey: rel(*this, (huey == 1) >> (dewey == 1))
Louie: "Dewey and I are not both guilty." -> not (dewey and louie): linear(*this, {dewey, louie}, IRT_LQ, 1)
Branching: the three flags, in the order of the output, BOOL_VAR_NONE / BOOL_VAL_MIN (the posts already fix all of them, so the search is trivial).
Objective: none (satisfaction).
