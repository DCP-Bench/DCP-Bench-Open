# general_store: cryptarithm. Each different letter stands for a different digit.
# The words above the line add up to ALL WOOL. Print the values of C, H, E, S, A, B, O, W, P, L.
# Each letter is an 8-bit bit-vector, so the column sums are bit-blasted to SAT; the integer
# outputs are read through BV2Int. The column sums (at most 16 digits of 9 plus a carry of 15)
# stay below 256, so 8 bits never overflow.
import cvc5.pythonic as cz

WIDTH = 8


def build(instance):
    names = ["C", "H", "E", "S", "A", "B", "O", "W", "P", "L"]
    letter = {n: cz.BitVec(n, WIDTH) for n in names}

    # Integers appear only in the outputs (BV2Int); the BV part is bit-blasted into the
    # main SAT solver, which proves that no second solution exists in seconds.
    solver = cz.SolverFor("ALL")
    solver.set("bv-solver", "bitblast-internal")

    # Each letter stands for a digit from 0 to 9.
    for n in names:
        solver.add(cz.ULE(letter[n], 9))

    # Each different letter stands for a different digit.
    solver.add(cz.Distinct(*[letter[n] for n in names]))

    # The words above the horizontal line represent numbers that add to the total of ALL WOOL.
    words = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
             "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
    total = "ALLWOOL"
    # Column by column from the units digit: the digits of the words in that column plus the
    # carry in equal the digit of the total plus ten times the carry out. A column holds at
    # most 16 digits, so a carry is at most 15; the leftmost column has no carry out.
    carry_in = cz.BitVecVal(0, WIDTH)
    for k in range(len(total)):
        column = carry_in
        for w in words:
            if len(w) > k:
                column = column + letter[w[-1 - k]]
        if k + 1 < len(total):
            carry_out = cz.BitVec(f"carry_{k + 1}", WIDTH)
            solver.add(cz.ULE(carry_out, 15))
        else:
            carry_out = cz.BitVecVal(0, WIDTH)
        solver.add(column == letter[total[-1 - k]] + 10 * carry_out)
        carry_in = carry_out

    outputs = {n: cz.BV2Int(letter[n]) for n in names}
    return solver, outputs
