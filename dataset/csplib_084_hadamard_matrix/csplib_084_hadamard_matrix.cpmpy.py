#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob084_hadamard_matrix.py
# Source description: https://www.csplib.org/Problems/prob084/

"""
For every odd positive integer \( \ell \) (and \( m = \frac{\ell - 1}{2} \)) we define the 2cc Hadamard matrix Legendre pairs CSP using the \{V, D, C\} format (Variables, Domains, Constraints) as follows:

- \( V = \{a_1, \ldots, a_\ell, b_1, \ldots, b_\ell\} \), a set of \( 2 \cdot \ell \) variables
- \( D = \{D_{a_1}, \ldots, D_{a_\ell}, D_{b_1}, \ldots, D_{b_\ell}\} \), a set of \( 2 \cdot \ell \) domains, all of them equal to \{-1, +1\}
- \( C = \{c_1, \ldots, c_m, c_{m+1}, c_{m+2}\} \), a set of \( m+2 \) constraints (\( m \) quadratic constraints and 2 linear constraints)

The \( m \) quadratic constraints are given by:
\[ c_s := \text{PAF}(A, s) + \text{PAF}(B, s) = -2, \forall s = 1, \ldots, m \]
where PAF denotes the periodic autocorrelation function: (\(i + s\) is taken mod \( \ell \) when it exceeds \( \ell \))
\[ A = [a_1, \ldots, a_\ell], \, \text{PAF}(A, s) = \sum_{i=1}^\ell a_i a_{i+s} \]
\[ B = [b_1, \ldots, b_\ell], \, \text{PAF}(B, s) = \sum_{i=1}^\ell b_i b_{i+s} \]

The 2 linear constraints are given by:
\[ c_{m+1} := a_1 + \ldots + a_\ell = 1 \]
\[ c_{m+2} := b_1 + \ldots + b_\ell = 1 \]

Print the variables a and b (a, b) as lists of l integers, with values either -1 or 1.
"""

# Data
l = 9  # Value of l (must be an odd positive integer)
# End of data

# Import libraries
import json
import numpy as np
from cpmpy import *

def PAF(arr, s):
    return sum(arr * np.roll(arr,-s))

def hadamard_matrix(l=5):

    m = int((l - 1) / 2)

    a = intvar(-1,1, shape=l, name="a")
    b = intvar(-1,1, shape=l, name="b")

    model = Model()

    model += a != 0 # exclude 0 from dom
    model += b != 0 # exclude 0 from dom

    model += sum(a) == 1
    model += sum(b) == 1

    for s in range(1,m+1):
        model += (PAF(a,s) + PAF(b,s)) == -2

    return model, (a,b)


# Example usage
model, (a, b) = hadamard_matrix(l)
model.solve()

# Print
solution = {"a": a.value().tolist(), "b": b.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
