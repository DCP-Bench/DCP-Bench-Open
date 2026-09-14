# csplib_024_langford

Two copies each of 1..k in a sequence of length 2k, the two copies of i exactly
i numbers apart.

- Instance input: `k`. Output: `sol` — 2k integers in 1..k. The reference's
  `position` array is auxiliary and is not a declared output.
- Satisfaction. Reference constraints: all_different(position);
  position[i+k] = position[i] + i + 1; sol[position[i]] = i for both copies,
  with position 0-based.
