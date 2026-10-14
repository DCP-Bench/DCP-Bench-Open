from pycsp3 import *

# A boy passes num_gates guards. At each gate he gives the guard half of his apples plus one,
# and the number given must be an integer. After the last gate he has one apple, which he gives the girl.
num_gates = data.num_gates

# apples[i] is the number of apples before gate i, and apples[num_gates] is the number after the last gate
# (the reference keeps the counts between 0 and 100)
apples = VarArray(size=num_gates + 1, dom=range(0, 101))

satisfy(
    # at each gate the boy keeps the apples left after paying half plus one; half must be an integer
    [apples[i] == 2 * apples[i + 1] + 2 for i in range(num_gates)],
    # after the last gate he has one apple left, which he gives the girl
    apples[num_gates] == 1,
)
