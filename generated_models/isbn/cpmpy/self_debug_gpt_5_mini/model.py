
import cpmpy as cp
import json
import sys

# Read input from stdin if provided. Expect either a JSON list like [9,7,8,-1,...]
# or a JSON object like {"isbn": [9,7,8,-1,...]}
data = None
s = sys.stdin.read().strip()
if s:
    try:
        parsed = json.loads(s)
        if isinstance(parsed, dict) and "isbn" in parsed:
            data = parsed["isbn"]
        elif isinstance(parsed, list):
            data = parsed
    except Exception:
        data = None

# Fallback example if no input given
if data is None:
    data = [9, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

# Basic validation
if not isinstance(data, list) or len(data) != 13:
    print("No solution found.")
    sys.exit(0)

given = data

# Create a (possibly unused) CPMpy model object as required by the guidelines.
model = cp.Model()

# weights for positions 0..11: 1,3,1,3,...
weights = [1 if i % 2 == 0 else 3 for i in range(12)]

# modular inverses modulo 10 for weights 1 and 3
inv_mod10 = {1: 1, 3: 7}  # since 3*7 = 21 ≡ 1 (mod 10)

def try_construct(third_choice):
    # Enforce prefix 9,7 and chosen third digit
    if given[0] != -1 and given[0] != 9:
        return None
    if given[1] != -1 and given[1] != 7:
        return None
    if given[2] != -1 and given[2] != third_choice:
        return None

    digits = [None] * 13
    digits[0] = 9
    digits[1] = 7
    digits[2] = third_choice

    # Fill known first 12 digits where given, and collect unknown positions (0..11)
    unknown_pos = []
    for i in range(12):
        if i in (0,1,2):
            # already set above
            if given[i] != -1 and given[i] != digits[i]:
                return None
            continue
        if given[i] != -1:
            if not isinstance(given[i], int) or not (0 <= given[i] <= 9):
                return None
            digits[i] = int(given[i])
        else:
            digits[i] = 0  # initial placeholder
            unknown_pos.append(i)

    # Compute current checksum from positions 0..11 with unknowns set to 0
    current_checksum = sum(weights[i] * digits[i] for i in range(12))
    current_mod = current_checksum % 10

    # Determine target modulo from given last digit (if any) or allow check digit to be computed
    last_given = given[12]
    if last_given != -1:
        if not isinstance(last_given, int) or not (0 <= last_given <= 9):
            return None
        # Need sum %10 == (-last_given) %10
        target_mod = (-last_given) % 10
        delta_mod = (target_mod - current_mod) % 10
        if delta_mod != 0:
            # Need to modify one unknown digit (if available) to achieve delta_mod
            if not unknown_pos:
                # no unknown in first 12 digits to adjust: impossible
                return None
            # try to find an unknown position where weight is 1 or 3 (all are)
            adjusted = False
            for pos in unknown_pos:
                w = weights[pos]
                inv = inv_mod10[w]
                v = (inv * delta_mod) % 10
                # v is in 0..9 and will satisfy (w*v) %10 == delta_mod
                # assign and done
                digits[pos] = v
                adjusted = True
                break
            if not adjusted:
                return None
        # Now compute final checksum and derived check digit and verify it equals last_given
        final_checksum = sum(weights[i] * digits[i] for i in range(12))
        check_digit = (10 - (final_checksum % 10)) % 10
        if check_digit != last_given:
            return None
        digits[12] = check_digit
    else:
        # last digit unknown -> compute it from the (possibly adjusted) checksum.
        # We will try to use no adjustments to inner digits first (we already set them to 0)
        final_checksum = sum(weights[i] * digits[i] for i in range(12))
        check_digit = (10 - (final_checksum % 10)) % 10
        digits[12] = check_digit

    # Finally ensure all given positions match
    for i in range(13):
        if given[i] != -1 and given[i] != digits[i]:
            return None

    # All digits filled with integers 0..9
    return [int(d) for d in digits]

# Try possible third-digit choices: if given[2] fixed, only try that; else try 8 then 9
third_candidates = [given[2]] if given[2] != -1 else [8, 9]

solution_digits = None
for c in third_candidates:
    sol = try_construct(c)
    if sol is not None:
        solution_digits = sol
        break

if solution_digits is not None:
    solution = {'isbn': [int(x) for x in solution_digits]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
