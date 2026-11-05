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
