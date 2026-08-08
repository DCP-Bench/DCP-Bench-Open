
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision variables for Across clues
A1 = cp.intvar(1, 10000, name="A1")
A4 = cp.intvar(1, 10000, name="A4")
A7 = cp.intvar(1, 10000, name="A7")
A8 = cp.intvar(1, 10000, name="A8")
A9 = cp.intvar(1, 10000, name="A9")
A10 = cp.intvar(1, 10000, name="A10")
A11 = cp.intvar(1, 10000, name="A11")
A13 = cp.intvar(1, 10000, name="A13")
A15 = cp.intvar(1, 10000, name="A15")
A17 = cp.intvar(1, 10000, name="A17")
A20 = cp.intvar(1, 10000, name="A20")
A23 = cp.intvar(2, 200, name="A23")  # prime number, domain limited for efficiency
A24 = cp.intvar(1, 10000, name="A24")
A25 = cp.intvar(1, 10000, name="A25")
A27 = cp.intvar(1, 10000, name="A27")
A28 = cp.intvar(1, 10000, name="A28")
A29 = cp.intvar(1, 10000, name="A29")
A30 = cp.intvar(1, 15000, name="A30")

# Decision variables for Down clues
D1 = cp.intvar(1, 15000, name="D1")
D2 = cp.intvar(1, 10000, name="D2")
D3 = cp.intvar(1, 20000, name="D3")
D4 = cp.intvar(1, 20000, name="D4")
D5 = cp.intvar(1, 10000, name="D5")
D6 = cp.intvar(1, 100000, name="D6")
D10 = cp.intvar(1, 10000, name="D10")
D12 = cp.intvar(1, 10000, name="D12")
D14 = cp.intvar(1, 10000, name="D14")
D16 = cp.intvar(1, 100000, name="D16")
D17 = cp.intvar(1, 100000, name="D17")
D18 = cp.intvar(1, 10000, name="D18")
D19 = cp.intvar(1, 10000, name="D19")
D20 = cp.intvar(1, 10000, name="D20")
D21 = cp.intvar(1, 10000, name="D21")
D22 = cp.intvar(1, 100000, name="D22")
D26 = cp.intvar(1, 10000, name="D26")
D28 = cp.intvar(1, 10000, name="D28")

# Constraints from clues:

# Across:
model += (A1 == A27 * 2)
model += (A4 == D4 + 71)
model += (A7 == D18 + 4)
model += (A8 * 16 == D6)  # 6 down divided by 16
model += (A9 == D2 - 18)
model += (A10 == 6 * 12 * 12)  # "Dozen in six gross" = 6*144=864
model += (A11 == D5 - 70)
model += (A13 == D26 * A23)
model += (A15 == D6 - 350)
model += (A17 == A25 * A23)
model += (A20 == A25 * 17)  # replaced modulo and division with multiplication
model += (A27 * 4 == D6)
model += (A28 == 48)  # Four dozen
model += (A29 == 7 * 144)  # Seven gross = 1008
model += (A30 == D22 + 450)

# Down:
model += (D1 == A1 + 27)
model += (D2 == 60)  # Five dozen
model += (D3 == A30 + 888)
model += (D4 == 2 * A17)
model += (D5 * 12 == A29)
model += (D6 == A28 * A23)
model += (D10 == A10 + 4)
model += (D12 == 3 * A24)
model += (D14 * 16 == A13)
model += (D16 == D28 * 15)
model += (D17 == A13 - 399)
model += (D18 * 18 == A29)
model += (D19 == D22 - 94)
model += (D20 == A20 - 9)
model += (D21 == A25 - 52)
model += (D22 == D20 * 6)
model += (D26 == 5 * A24)
model += (D28 == D21 + 27)

# Additional constraints for primality and squares:

# Primes up to 200 for A23
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
          53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109,
          113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179,
          181, 191, 193, 197, 199]
model += cp.Table([A23], [[p] for p in primes])

# Squares up to 10000 for A20 and A24
squares = [i*i for i in range(1, 101)]
model += cp.Table([A20], [[s] for s in squares])
model += cp.Table([A24], [[s] for s in squares])

# Solve the model
if model.solve():
    # Map clue numbers to their values
    clue_values = {
        1: int(A1.value()),
        2: int(D2.value()),
        3: int(D3.value()),
        4: int(A4.value()),
        5: int(D5.value()),
        6: int(D6.value()),
        7: int(A7.value()),
        8: int(A8.value()),
        9: int(A9.value()),
        10: int(A10.value()),
        11: int(A11.value()),
        12: int(D12.value()),
        13: int(A13.value()),
        15: int(A15.value()),
        16: int(D16.value()),
        17: int(A17.value()),
        18: int(D18.value()),
        19: int(D19.value()),
        20: int(A20.value()),
        21: int(D21.value()),
        22: int(D22.value()),
        23: int(A23.value()),
        24: int(A24.value()),
        25: int(A25.value()),
        26: int(D26.value()),
        27: int(A27.value()),
        28: int(A28.value()),
        29: int(A29.value()),
        30: int(A30.value()),
    }

    # The grid from the problem statement (rows 1 to 9, columns 1 to 9)
    # Using 0 for blocked cells (X) and empty cells
    # Positions with clue numbers replaced by their values

    # Row 1:  1  2  _  3  X  4  _  5  6
    # Row 2:  7  _  X  8  _  _  X  9  _
    # Row 3:  _  X 10  _  X 11 12  X  _
    # Row 4: 13 14 _  _  X 15 _ 16 _
    # Row 5:  X  _  X  X  X  X  X  _  X
    # Row 6: 17 _ 18 19 X 20 21 _ 22
    # Row 7:  _  X 23 _  X 24 _  X  _
    # Row 8: 25 26 X 27 _  _  X 28 _
    # Row 9: 29 _  _  _  X 30 _  _  _

    # Note: Clue 14 across is not defined, so replaced by 0
    # Clue 12 down is D12, clue 16 down is D16, clue 14 down is D14 (not in grid)
    # Clue 14 across is missing, so 0

    M = [
        [clue_values[1], clue_values[2], 0, clue_values[3], 0, clue_values[4], 0, clue_values[5], clue_values[6]],
        [clue_values[7], 0, 0, clue_values[8], 0, 0, 0, clue_values[9], 0],
        [0, 0, clue_values[10], 0, 0, clue_values[11], clue_values[12], 0, 0],
        [clue_values[13], 0, 0, 0, 0, clue_values[15], 0, clue_values[16] if 16 in clue_values else 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [clue_values[17], 0, clue_values[18], clue_values[19], 0, clue_values[20], clue_values[21], 0, clue_values[22]],
        [0, 0, clue_values[23], 0, 0, clue_values[24], 0, 0, 0],
        [clue_values[25], clue_values[26], 0, clue_values[27], 0, 0, 0, clue_values[28], 0],
        [clue_values[29], 0, 0, 0, 0, clue_values[30], 0, 0, 0],
    ]

    # Print solution as JSON
    solution = {'M': M}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
