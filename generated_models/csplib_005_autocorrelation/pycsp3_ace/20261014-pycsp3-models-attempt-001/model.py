from pycsp3 import *

# binary sequence of length n with values -1 and +1, minimising the sum of the squared periodic autocorrelations
n = data.n

# sequence[i] is the bit at position i, -1 or +1
sequence = VarArray(size=n, dom={-1, 1})

# product[k - 1][i] is sequence[i] * sequence[(i + k) mod n], for shift k from 1 to n - 1
product = VarArray(size=[n - 1, n], dom={-1, 1})

# corr[k - 1] is the periodic autocorrelation C_k, and square[k - 1] is C_k squared
corr = VarArray(size=n - 1, dom=range(-n, n + 1))
square = VarArray(size=n - 1, dom=range(0, n * n + 1))

satisfy(
    # the product of two bits is +1 when they are equal and -1 when they differ
    [Table(scope=[sequence[i], sequence[(i + k) % n], product[k - 1][i]],
           supports=[(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)])
     for k in range(1, n) for i in range(n)],
    # the k-th periodic autocorrelation is the sum of the products of the bits k places apart
    [corr[k - 1] == Sum(product[k - 1]) for k in range(1, n)],
    # the square of each autocorrelation
    [Table(scope=[corr[k - 1], square[k - 1]], supports=[(c, c * c) for c in range(-n, n + 1)])
     for k in range(1, n)],
)

# minimise the energy, the sum of the squares of the autocorrelations
minimize(Sum(square))
