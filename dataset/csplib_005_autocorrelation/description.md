These problems have many practical applications in communications and electrical engineering. The objective is to
construct a binary sequence of length n that minimizes the autocorrelations between bits. Each bit in the sequence
takes the value +1 or -1. With non-periodic (or open) boundary conditions, the k-th autocorrelation, Ck is defined to
be \[ C_k = \sum_{i=0}^{n-k-1} S_i \cdot S_{i+k} \]. With periodic (or cyclic) boundary conditions, the k-th
autocorrelation, Ck is defined to be \[ C_k = \sum_{i=0}^{n-1} S_i \cdot S_{(i+k) \mod n} \]. This problem uses the periodic
ones: the aim is to minimize the sum of their squares, that is, to minimize \[ E = \sum_{k=1}^{n-1} C_k^2 \].

Print the binary sequence (sequence) as a list of integers, where -1 represents a bit value of -1 and 1 represents a bit value of +1.
