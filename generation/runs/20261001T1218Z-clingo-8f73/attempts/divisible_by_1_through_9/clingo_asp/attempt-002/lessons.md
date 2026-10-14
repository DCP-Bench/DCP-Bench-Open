Blocker evidence for clingo_asp (measured):

The reference answer is a 10-digit number. The only pandigital number with the property has the
last digit 0 (divisibility by 10), so a leading 0 is impossible, and the value is above 2^31 - 1.
clingo integers are 32 bits and the runner reads shown atoms with symbol.number, so number(N) cannot
carry it.

attempt-001 builds the prefixes up to ten digits: the evaluator reports no_solution / status unsat
(the 10th step overflows 32 bits in the grounder). attempt-002 stops at the first nine digits, which
fit: the evaluator receives one solution and reports invalid_solution (a 9-digit value cannot extend
to the reference's 10-digit one).
