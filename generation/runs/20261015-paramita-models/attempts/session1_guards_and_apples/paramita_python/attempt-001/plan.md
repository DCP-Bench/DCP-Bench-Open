# Plan: guards and apples (boy passes num_gates gates, bribes each guard with half his apples plus one)
- number of apples before each gate and after the last gate, a_0..a_n -> binary integers (bits, weights 2^k)
- half of his apples given to the guard at each gate, h_i (integer, binary bits)
- he gives the guard an integer number of apples -> a_i == 2 * h_i for each gate
- gives half plus one: a_{i+1} + h_i + 1 == a_i for each gate
- after the last gate he still holds the one apple he gives the girl, and then has none -> a_n == 1
- Bit width: a_0 = 3*2**n - 2 at most (forced chain from a_n = 1: a_i + 2 = 2*(a_{i+1} + 2)), so n+2 bits suffice
- Objective: none (satisfaction). Output apples as the list a_0..a_n of integer expressions.
