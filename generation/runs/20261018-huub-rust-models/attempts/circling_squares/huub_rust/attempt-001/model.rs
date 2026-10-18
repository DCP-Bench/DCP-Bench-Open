// Circling the squares: place a different number in each of the ten squares A, B, C, D, E, F, G, H, I, K,
// arranged in a circle in that order. The sum of the squares of any two adjacent numbers shall be equal to
// the sum of the squares of the two numbers diametrically opposite to them. Fractions are not allowed,
// and no number needs more than two figures.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // each of the ten squares holds a number between 0 and 99 (no more than two figures)
    let x = m.new_int_decisions(10, 0..=99);

    // a different number in each of the ten squares
    m.unique(x.clone()).post()?;

    // the four numbers placed as examples stand as they are: A=16, B=2, F=8, G=14
    m.linear(x[0]).eq(16).post()?;
    m.linear(x[1]).eq(2).post()?;
    m.linear(x[5]).eq(8).post()?;
    m.linear(x[6]).eq(14).post()?;

    // the square of each number, as a variable
    let mut sq = Vec::new();
    for &v in &x {
        let s = m.new_int_decision(0..=9801);
        m.pow(v, 2).result(s).post()?;
        sq.push(s);
    }

    // the sum of the squares of any two adjacent numbers equals the sum of the squares of the two
    // numbers diametrically opposite to them (A and B to F and G, B and C to G and H, and so on)
    for i in 0..10 {
        let j = (i + 1) % 10;
        let k = (i + 5) % 10;
        let l = (i + 6) % 10;
        m.linear(sq[i] + sq[j] - sq[k] - sq[l]).eq(0).post()?;
    }

    let mut out = Out::new();
    out.put("A", x[0])
        .put("B", x[1])
        .put("C", x[2])
        .put("D", x[3])
        .put("E", x[4])
        .put("F", x[5])
        .put("G", x[6])
        .put("H", x[7])
        .put("I", x[8])
        .put("K", x[9]);
    Ok(out)
}
