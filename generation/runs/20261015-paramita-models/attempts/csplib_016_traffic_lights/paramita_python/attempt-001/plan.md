# Plan: csplib_016 traffic lights

- each vehicle light V1..V4 has one of 4 states (0 red, 1 red-yellow, 2 green, 3 yellow) -> one-hot Bools V[i][s], sum == 1
- each pedestrian light P1..P4 has one of 2 states (0 red, 1 green) -> one-hot Bools P[i][s], sum == 1
- for each i = 1..4 (cyclic, light 5 = light 1), (V_i, P_i, V_i+1, P_i+1) is one of the allowed tuples -> one Bool per allowed tuple t, sum(tb) == 1, If(tb, all four one-hot literals match t)
- output lights = [V1..V4, P1..P4] -> sum(s * V[i][s]) and sum(s * P[i][s])
- objective -> satisfaction (no objective)
