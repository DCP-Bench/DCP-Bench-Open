Read the whole description before counting: "after giving the apple to the girl, he has no apples left" means one apple remains after the last gate, so the output ends in 1, not 0. The brief's example lists fix the count only through the description.
The bound 3*2^n - 2 for the start count comes from the reverse recurrence a_i = 2*(a_{i+1}+1) from a_n = 1, and it is exact.
The 2*bribe == apples + 2 form makes the integer-bribe condition a single linear equality.
