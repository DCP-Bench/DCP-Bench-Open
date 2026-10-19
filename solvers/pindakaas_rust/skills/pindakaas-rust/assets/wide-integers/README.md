# wide-integers

Numbers of up to 62 bits held as literals, constrained through an adder network: `3x + 7y = 10^15` over `0..=10^15` enumerated with blocking clauses over the bits, and a divisibility condition on a 12-digit number. An `IntVar` of such a domain aborts the process.

```bash
cargo run --release
```
