# csplib_006_golomb_rulers

A ruler with `size` marks, 0 = a1 < a2 < ... , whose pairwise differences are
all distinct, of minimum length.

- Instance input: `size`. Outputs: `marks` (size integers in 0..size*size) and
  `length`, which the reference declares as `marks[-1]`.
- Minimize `length`. The reference's symmetry breaking is commented out.
