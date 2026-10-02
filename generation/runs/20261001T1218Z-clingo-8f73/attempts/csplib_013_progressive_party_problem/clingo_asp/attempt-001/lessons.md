# Lesson from the first attempt (rejected with `parsing failed`)

`2 { P : visits(P,B1,V), visits(P,B2,V) }` is not a count. In a body, `lower { ... }` takes
literals as elements, and `P` is a term, so gringo fails with the bare message `parsing failed`.
Write `#count { P : ... } >= 2` instead. The clingo-asp skill says cardinality bounds go outside
the braces but does not say the elements must then be literals.
