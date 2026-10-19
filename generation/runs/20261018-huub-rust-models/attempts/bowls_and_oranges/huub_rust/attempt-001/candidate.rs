// Bowls and oranges: m oranges are placed in n bowls, all in a line at 1 m intervals
// (bowls numbered 1..=n). No more than one orange per bowl. No three oranges A, B, C
// with distance(A, B) equal to distance(B, C).
// Output x: the bowls holding the oranges, in ascending order.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let k = inst.size("m");

    // Place the oranges in bowls 1..=n, one orange per bowl, listed in ascending order.
    let mut x: Vec<View<i64>> = Vec::with_capacity(k);
    for _ in 0..k {
        x.push(m.new_int_decision(1..=n));
    }
    for i in 1..k {
        m.linear(x[i - 1] - x[i]).le(-1).post()?;
    }

    // No three oranges A, B, C with distance(A, B) equal to distance(B, C):
    // for bowls x[i] < x[j] < x[l] in ascending order, x[i] + x[l] != 2 * x[j].
    for i in 0..k {
        for j in (i + 1)..k {
            for l in (j + 1)..k {
                m.linear(x[i] + x[l] - x[j] * 2).ne(0).post()?;
            }
        }
    }

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
