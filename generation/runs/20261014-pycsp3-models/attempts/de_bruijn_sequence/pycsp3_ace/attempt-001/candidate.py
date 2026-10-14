from pycsp3 import *

base = data.base
n = data.n
size = base ** n

# the sequence is cyclic: position i holds one symbol of the alphabet 0 to base-1
de_bruijn = VarArray(size=size, dom=range(base))

# the length-n string starting at position i, read as a number in base `base`
windows = VarArray(size=size, dom=range(base ** n))

satisfy(
    # the window starting at position i is the number formed by the n cyclic symbols from i on
    [windows[i] == Sum(de_bruijn[(i + j) % size] * base ** (n - 1 - j) for j in range(n)) for i in range(size)],
    # every length-n string occurs exactly once, so all windows are different
    AllDifferent(windows),
    # the cyclic sequence can start at its all-zero string, so the first n symbols are zero
    [de_bruijn[j] == 0 for j in range(n)],
)
