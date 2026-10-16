Four-way junction with eight lights: four vehicle lights V1..V4 (states 0..3) and four pedestrian lights P1..P4 (states 0..1).
  -> V = intVarArray 0..3, P = intVarArray 0..1, lights = V then P (output order V1..V4, P1..P4)
The lights have different states; the safe combinations (V_i, P_i, V_i+1, P_i+1) for i=1..4 with V_5=V_1, P_5=P_1.
  -> for each i in 0..3: m.table((V_i, P_i, V_(i+1 mod 4), P_(i+1 mod 4)), Tuples of allowed_tuples) .post()
Every other combination is disallowed to prevent accidents.
  -> Tuples(true): only the instance's allowed tuples are admitted
Print a valid 8-tuple of light states as [V1..V4, P1..P4].
  -> declared output "lights" = IntVar[8]; satisfaction, no objective
