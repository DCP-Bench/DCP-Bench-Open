Imagine a four-way traffic junction with eight traffic lights. Four lights (V1 to V4) are for vehicles, and four (P1 to P4)
are for pedestrians. The lights have different states (e.g., red, green). The problem parameters list the combinations of
light states (V_i, P_i, V_{i+1}, P_{i+1}) that are safe for intersecting roads, for i=1..4 (with V_5=V_1 and P_5=P_1);
every other combination is disallowed to prevent accidents.

Vehicle light states: 0=red, 1=red-yellow, 2=green, 3=yellow
Pedestrian light states: 0=red, 1=green

Print a valid 8-tuple of light states (lights) as a list of integers with the order [V1, V2, V3, V4, P1, P2, P3, P4].
