# Sources for `pindakaas-rust`

Tested with pindakaas 0.6.0 (crate, MPL-2.0, released 2026-10-13), Rust 1.98.1 and g++ 12.2
on Linux with Docker. The skill text is Apache-2.0.

Existing skills: not searched for beyond the spike that preceded this skill. Run
`npx skills find pindakaas` before a public release.

Documentation this skill's instructions were written from:

- <https://crates.io/crates/pindakaas> — the crate, version 0.6.0, licence MPL-2.0.
- <https://docs.rs/pindakaas/0.6.0/pindakaas/> — the crate-level API reference.
- <https://github.com/pindakaashq/pindakaas> — repository and changelog.
- The crate sources of `pindakaas` 0.6.0 (fetched with `cargo fetch` in a Rust 1.98.1
  container). Every signature in this skill was read from them: `lib.rs`
  (`ClauseDatabaseTools::encode_implied`, `add_clause`, `new_lit`), `decision/integer.rs`
  (`IntVar::new`, `at_least`, `at_most`, `equals`, `value`), `constraint/linear.rs`
  (`Linear`, `LinExp`, `Comparator`, `LinearEncoder`, `StaticLinEncoder`), and `solver.rs`
  (`SolveResult`, `Assumptions`, `TerminateCallback`, `TermSignal`).

Every claim below was checked by compiling and running it, not from documentation alone.

- Defaults: `StaticLinEncoder` is MixedRadix for integer sums, Totalizer for pseudo-Boolean,
  cardinality and count constraints, and Product for at-most-one.
- `encode_implied` over integer terms narrows the variables: `b -> x + y <= 4` with `b`
  false leaves 25 of 36 pairs, `b -> x - y == 1` leaves 30 of 36. With encodings already
  present it panics ("a direct encoding holds for one of its values"). Over a sum of
  literals it is correct. The `define` form keeps all 51 solutions of `b -> x + y <= 4`.
- `IntVar::value` of a variable with no encoding returns the domain minimum.
- An `IntVar` encoded in one solver and reused in a second one gives wrong answers
  (`x >= 3` in the first, `x <= 1` in the second: the second is satisfiable with `x = 0`).
- `i64` overflow is silent: `2^61 x + 2^61 y <= 2^62` over `0..4` accepts all 25 pairs, six
  of which are correct. Coefficients of 10^12 on small domains are fine.
- A zero coefficient on an `IntVar` term panics inside the aggregator; on a literal it is fine.
- Wide domains: `3x + 7y = N + 1` with the default encoders takes 3.1 s and 4.8 million
  variables at `N = 10^7`, and aborts with a C++ `bad_alloc` at `N = 10^9`. The adder encoder
  handles `10^9` (254 variables) until an order or equality view of a wide variable is built.
- `set_terminate_callback` stops the search 0.4 ms after the deadline (46,500 polls in 2 s,
  largest gap 7.6 ms); the solver can be solved again after an interrupt. Encoding is not
  interruptible: one Totalizer bound took about 10 s and overran a 20 s deadline.
- Kissat aborts the process (exit 134, "Coverage goal solver->level reached") on a clause
  added after a solve.
- Linear search with `solve_assuming` and an order literal as the assumption proves a minimum;
  a bound that is `BoolVal::Const(false)` means the domain has no better value.
- Panics: `IntVar::new(5..=3)` (later, when a bound is taken), `CardinalityOne::new` with `a`
  and `!a`, `from_*_encoding` with a wrong number of literals.
- Timings, one machine under load: 8-queens all 92 solutions in 28 ms, 12-queens all 14,200 in
  14 s, order-3 magic squares all 8 in 11 ms, Golomb ruler of 8 marks proven optimal in 3.4 s.
