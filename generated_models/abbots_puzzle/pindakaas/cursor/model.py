from pindakaas.solver import CaDiCaL, Status
import json

# Integers 0..100 as 8-bit unsigned values (binary encoding).
NBITS = 8
WEIGHTS = [2 ** i for i in range(NBITS)]
solver = CaDiCaL()


def int_bits():
    return list(solver.new_vars(NBITS))


def int_value(bits):
    return sum(w * bit for w, bit in zip(WEIGHTS, bits))


# Decision variables: number of men, women, and children
men, women, children = int_bits(), int_bits(), int_bits()
solver.add_encoding(int_value(men) <= 100)
solver.add_encoding(int_value(women) <= 100)
solver.add_encoding(int_value(children) <= 100)

# 100 people in total
solver.add_encoding(int_value(men) + int_value(women) + int_value(children) == 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
solver.add_encoding(6 * int_value(men) + 4 * int_value(women) + int_value(children) == 200)
# Five times as many women as men
solver.add_encoding(int_value(women) - 5 * int_value(men) == 0)

with solver.solve() as result:
    if result.status != Status.SATISFIED:
        raise SystemExit("No solution found.")

    def decode(bits):
        return sum(w for w, bit in zip(WEIGHTS, bits) if result.value(bit))

    print(json.dumps({
        "men": decode(men),
        "women": decode(women),
        "children": decode(children),
    }))
