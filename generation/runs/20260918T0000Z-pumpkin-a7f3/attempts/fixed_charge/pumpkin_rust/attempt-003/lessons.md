# fixed_charge

attempt-001 failed to compile: a local was named `use`, which is a Rust keyword.
The diagnostic was misleading -- rustc reported "ergonomic clones are
experimental" and pointed at a closure body -- so the real cause is worth
recording: a keyword used as an identifier in a closure. Renamed to `usage`.

attempt-002 was accepted but capped production with `rent[product[p][1]]`, the
machine the product needs. The reference writes `rent[p]`, indexing by the
product instead. Both agree on the listed instance, because product p happens to
use machine p there, so the evaluator could not tell them apart. attempt-003
posts `rent[p]`, which is what the reference specifies.

The retention check also refuses this model for not reading `shirt`, `shorts`,
`pants`, `shirtM`, `shortM`, `pantM`, `products`, `machines` and `resources`.
Waived after checking the reference: those are index constants, used only to
enumerate (`for p in products`), and each list is exactly `0..len - 1`. The
model enumerates the same ranges from `num_products`, `num_machines` and the
length of `capacity`. A comment in the model says so.
