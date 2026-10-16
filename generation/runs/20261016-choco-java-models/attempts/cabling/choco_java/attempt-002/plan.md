Place the n devices in n consecutive rack slots, one device per slot -> pos_d in 1..n, allDifferent "AC".
Each cable between devices a and b, cable_struct [a, b, count] -> length of one cable = |pos_a - pos_b| (pos_a.dist(pos_b).intVar()).
Sum of all cable lengths (count copies each) -> scalar(lengths, counts, "=", total).
Objective: minimize total (final_sum). Read cable_struct through raw() because the brief marks it unbindable (mixed str/int rows).
