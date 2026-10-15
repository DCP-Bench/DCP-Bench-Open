The Aircraft Landing Problem involves scheduling the landing of a set of aircraft on a single runway.
  -> one integer landing time per aircraft (landing_times[i]), in the fixed sequence of the instance (index order)
Each aircraft has a specified time window (earliest and latest possible landing time).
  -> per aircraft i: binary encoding, landing = earliest + sum(2^k * bit); landing <= latest (only when the bits can exceed the width)
Penalties are incurred for landing earlier or later than the target time.
  -> per aircraft: binary deviations early >= target - landing and late >= landing - target (only when they can be positive); penalty = penalty_before * early + penalty_after * late
A minimum separation time between the landings of any two aircraft must be respected.
  -> per pair i < j (fixed sequence): landing_j >= landing_i + separation_time[i][j] (PB over binary bits)
This specific problem instance assumes a fixed landing sequence.
  -> only pairs i < j get a separation constraint (the sequence is the index order)
The objective is to determine the exact landing time for each aircraft to minimize the total penalty.
  -> minimize sum_i (penalty_before_i * early_i + penalty_after_i * late_i)
Print the landing time for each aircraft (landing_times) and the minimized total penalty (total_penalty).
  -> outputs landing_times[i] (integer expression) and total_penalty (the objective expression)
Encoding change after a rejected quick check: order (unary) bits over the time window ran out of memory on airland1 (PB separation) and crashed the runner on airland2 when the optimum was fixed; binary is used instead.
