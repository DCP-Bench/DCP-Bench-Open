// Clock triplets: rearrange the numbers 1 to 12 on the face of a clock (a ring of 12
// positions) so that no triplet of adjacent numbers has a sum higher than 21.
// Output x: the 12 numbers in clock order.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = 12usize;

    // Rearrange the numbers on the face of a clock (1 to 12): each number is used once.
    let x: Vec<IntVar> = (0..n).map(|_| IntVar::new(1..=12)).collect();
    all_different(s, &x)?;

    // No triplet of adjacent numbers has a sum higher than 21, the clock wraps around.
    for i in 0..n {
        let a = &x[i];
        let b = &x[(i + 1) % n];
        let c = &x[(i + 2) % n];
        post(s, iv(a) + iv(b) + iv(c), Comparator::LessEq, 21)?;
    }

    // Print the arrangement of the numbers on the clock (x).
    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
