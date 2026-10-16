Vehicle lights V1..V4 take states 0=red, 1=red-yellow, 2=green, 3=yellow -> IntVar domains 0..3 on lights[0..3]
Pedestrian lights P1..P4 take states 0=red, 1=green -> IntVar domains 0..1 on lights[4..7]
For i=1..4 with V5=V1, P5=P1, the tuple (V_i, P_i, V_i+1, P_i+1) must be one of the safe combinations of the instance -> extensional(*this, x_i, TupleSet of allowed_tuples) with TupleSet finalized (domain consistent)
Every other combination is disallowed -> covered by the extensional table (only listed tuples are allowed)
Branching: branch on all 8 light variables, first fail (INT_VAR_SIZE_MIN), smallest value first (INT_VAL_MIN)
Objective: none (satisfaction); output lights as the 8-tuple [V1..V4, P1..P4]
