// Clock triplets: rearrange the numbers 1 to 12 on the face of a clock so that
// no triplet of adjacent numbers has a sum higher than 21. The face is a circle,
// so the triplets wrap around from 12 back to 1.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // The numbers on the clock face are 1 to 12, each used exactly once.
    let x = m.new_int_decisions(12, 1..=12);
    m.unique(x.clone()).post()?;

    // No triplet of adjacent numbers has a sum higher than 21.
    for i in 0..12 {
        let a = x[i];
        let b = x[(i + 1) % 12];
        let c = x[(i + 2) % 12];
        m.linear(a + b + c).le(21).post()?;
    }

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
