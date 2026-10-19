# Cryptarithm SEND + MORE = MONEY: give each letter one digit so that different letters get
# different digits, the leading letters S and M are not 0, and the sum is correct.
# Method: a one-hot binary per letter and digit. A letter's value is the sum of digit * binary,
# so the sum is one linear equation over the letter values. At most one letter per digit.
import mip

letters = "SENDMORY"
leading = "SM"
send = [("S", 1000), ("E", 100), ("N", 10), ("D", 1)]
more = [("M", 1000), ("O", 100), ("R", 10), ("E", 1)]
money = [("M", 10000), ("O", 1000), ("N", 100), ("E", 10), ("Y", 1)]

m = mip.Model(solver_name="CBC")
m.verbose = 0
x = {(L, d): m.add_var(f"x_{L}_{d}", var_type=mip.BINARY) for L in letters for d in range(10)}

# each letter takes exactly one digit
for L in letters:
    m += mip.xsum(x[L, d] for d in range(10)) == 1

# leading letters are not 0
for L in leading:
    m += x[L, 0] == 0

# different letters take different digits: each digit is used by at most one letter
for d in range(10):
    m += mip.xsum(x[L, d] for L in letters) <= 1

# the letter's value is the digit it takes
value = {L: mip.xsum(d * x[L, d] for d in range(10)) for L in letters}

# SEND + MORE = MONEY as one linear equation over the letter values
m += mip.xsum(w * value[L] for L, w in send + more) == mip.xsum(w * value[L] for L, w in money)

# no objective: any assignment that satisfies the equation answers the puzzle
status = m.optimize(max_seconds=60)
if status == mip.OptimizationStatus.OPTIMAL:
    digit = {L: next(d for d in range(10) if x[L, d].x > 0.5) for L in letters}
    word = lambda ws: int("".join(str(digit[L]) for L in ws))
    s, mo, mon = word("SEND"), word("MORE"), word("MONEY")
    print(f"SEND + MORE = MONEY: {s} + {mo} = {mon}")
    print("digits:", " ".join(f"{L}={digit[L]}" for L in letters))
else:
    print("Status:", status.name)
