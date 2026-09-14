# csplib_024_langford

Arrange two copies each of 1..k in a sequence of length 2k so that the two
copies of i are i numbers apart (i.e. i+1 positions apart).

- Instance input: `k`.
- Output: `sol` — 2k integers in 1..k. (`position` is auxiliary in the reference
  and is NOT a declared output.)
- Satisfaction. Reference constraints, with `position[j]` 0-based over 0..2k-1:
  AllDifferent(position); position[i+k-1] = position[i-1] + i + 1;
  sol[position[i-1]] = i and sol[position[k+i-1]] = i, for i = 1..k.
- The reference's symmetry breaking is commented out; not carried over.
