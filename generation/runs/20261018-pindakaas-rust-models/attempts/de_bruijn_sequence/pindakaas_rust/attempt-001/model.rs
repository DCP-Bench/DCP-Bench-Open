// de Bruijn sequence B(k, n): a cyclic sequence over the alphabet {0, ..., k-1}
// of length k^n in which every possible length-n string occurs exactly once as a
// (cyclic) substring. Output: the sequence as a list of k^n integers.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let k = inst.int("base");
    let n = inst.size("n");
    let len = k.pow(n as u32) as usize;

    // The sequence: one digit per position, alphabet 0..k-1.
    let x: Vec<IntVar> = (0..len).map(|_| IntVar::new(0..=k - 1)).collect();

    // Each window of n consecutive positions (wrapping around the cycle) is read
    // as a base-k number in 0..k^n-1.
    // Each length-n string occurs exactly once as a cyclic substring: the k^n
    // windows take pairwise distinct values.
    let mut windows: Vec<IntVar> = Vec::with_capacity(len);
    for i in 0..len {
        // The window starting at position i, read as a base-k number.
        let mut e = LinExp::default();
        for j in 0..n {
            let weight = k.pow((n - 1 - j) as u32);
            e += scaled(&x[(i + j) % len], weight);
        }
        windows.push(define(s, e)?);
    }
    // Every length-n string occurs exactly once.
    all_different(s, &windows)?;

    let mut out = Out::new();
    out.put("de_bruijn", &x);
    Ok(out)
}
