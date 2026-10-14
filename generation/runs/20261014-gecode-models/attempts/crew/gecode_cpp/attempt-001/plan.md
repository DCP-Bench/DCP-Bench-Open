Assign 20 flight attendants to 10 flights.
Each flight needs a certain number of cabin crew -> linear(*this, row of works(f,*), IRT_EQ, required[f][0]) per flight
they have to speak certain languages -> linear(*this, qualified(f,j), IRT_GQ, required[f][j+1]) per flight and per attribute (steward, hostess, French, Spanish, German); qualified = attendants with attribute j
Every cabin crew member has two flights off after an attended flight -> per attendant, linear(*this, window of 3 consecutive flights, IRT_LQ, 1) (at most one attended flight per 3 consecutive; equivalent to "attended at f => f+1, f+2 off"; windows cut at the last flight)
Branching: BOOL_VAR_NONE over works in flight order, BOOL_VAL_MIN.
Objective: none (satisfaction); output crew as one list of 20 Booleans per flight.
