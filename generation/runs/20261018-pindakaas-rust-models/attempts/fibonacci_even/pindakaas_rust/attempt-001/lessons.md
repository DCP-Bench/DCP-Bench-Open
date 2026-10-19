# fibonacci_even, pindakaas_rust: lessons

Result: rejected, `no_instance_verified` (memory_limit, 2048 MB). Not retained.

- The output `res` is the sum of even terms up to 4,000,000, so its value is 4,613,732. The
  declared int output needs an `IntVar` whose domain reaches about 8 * 10^6 (two times the bound).
- Each Fibonacci term was modelled as a 23-bit vector with ripple-carry adders. The adders
  alone are cheap: with `res` as an `IntVar` of domain 0..=1000 and no link, the runner
  reports `invalid_solution` (not a memory failure).
- The memory cost is the `IntVar` output. An unlinked `IntVar::new(0..=2_000_000)` already
  exceeds 2 GB, and so does 0..=8_000_000 with or without the bit-sum link. The harness's
  equality view on each integer output appears to build the order encoding over the whole domain.
- Earlier variant with one `IntVar` (domain 0..=4*10^6) per term, linked by `mod_const` and
  `post_if`, also exceeded 2 GB within seconds.
- No formulation found that keeps `res` in a small domain while still carrying its value.
  Unverified: whether a sparse domain (`RangeList`) avoids the cost; it would need the set of
  achievable sums and was not tried.
