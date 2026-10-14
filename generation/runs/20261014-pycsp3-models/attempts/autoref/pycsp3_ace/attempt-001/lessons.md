The description allows s entries above n (for n=3, m=0 it also admits (4,0,0,0,0)); the reference admits only s_i <= n, so the second enumerated solution failed with invalid_solution 'Declared outputs cannot extend to a reference solution'.
Fix: bound the entries by max(n, m). Checking with --solution-limit 2 found this; limit 1 hid it.
