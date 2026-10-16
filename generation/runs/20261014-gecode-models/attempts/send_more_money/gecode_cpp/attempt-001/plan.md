each letter represents a unique digit -> distinct(*this, x, IPL_DOM) over the eight letters s,e,n,d,m,o,r,y
each letter must be assigned a digit from 0 to 9 -> IntVar domains 0..9
the first letter of each word cannot be zero -> rel(*this, s != 0), rel(*this, m != 0)
the equation SEND + MORE = MONEY holds -> linear(*this, IntArgs(w), vars, IRT_EQ, 0) with weights 1000s+100e+10n+d+1000m+100o+10r+e-10000m-1000o-100n-10e-y (weights collected per letter; one linear over the eight letters, IPL_DOM as the default bounds is enough for this size)
the branching -> INT_VAR_SIZE_MIN, INT_VAL_MIN over the eight letters
the objective -> none (satisfaction)
