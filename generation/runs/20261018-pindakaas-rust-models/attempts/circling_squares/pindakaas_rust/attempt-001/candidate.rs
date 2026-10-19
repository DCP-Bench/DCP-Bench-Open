// Circling the squares: place a number in each of the ten squares A, B, C, D, E, F, G, H, I, K
// arranged on a circle in that order. Fill in integers without fractions, each with at most
// two figures. A=16, B=2, F=8, G=14 are fixed.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Fractions are not allowed, and no number need contain more than two figures.
    let xs: Vec<IntVar> = (0..10).map(|_| IntVar::new(0..=99)).collect();

    // The four numbers placed, as examples, must stand as they are.
    post(s, iv(&xs[0]), Comparator::Equal, 16)?; // A
    post(s, iv(&xs[1]), Comparator::Equal, 2)?; // B
    post(s, iv(&xs[5]), Comparator::Equal, 8)?; // F
    post(s, iv(&xs[6]), Comparator::Equal, 14)?; // G

    // Place a different number in each of the ten squares.
    all_different(s, &xs)?;

    // The sum of the squares of any two adjacent numbers shall be equal to the sum of the
    // squares of the two numbers diametrically opposite to them. The pair starting at i has
    // the pair starting at i + 5 opposite to it. Each such equation is a table over the four
    // numbers, so no sum over wide variables is encoded.
    let mut quad: Vec<Vec<i64>> = Vec::new();
    for a in 0..=99i64 {
        for b in 0..=99i64 {
            for c in 0..=99i64 {
                for d in 0..=99i64 {
                    if a * a + b * b == c * c + d * d {
                        quad.push(vec![a, b, c, d]);
                    }
                }
            }
        }
    }
    for i in 0..5 {
        let cols = [
            xs[i].clone(),
            xs[(i + 1) % 10].clone(),
            xs[(i + 5) % 10].clone(),
            xs[(i + 6) % 10].clone(),
        ];
        table(s, &cols, &quad)?;
    }

    let mut out = Out::new();
    out.put("A", &xs[0]);
    out.put("B", &xs[1]);
    out.put("C", &xs[2]);
    out.put("D", &xs[3]);
    out.put("E", &xs[4]);
    out.put("F", &xs[5]);
    out.put("G", &xs[6]);
    out.put("H", &xs[7]);
    out.put("I", &xs[8]);
    out.put("K", &xs[9]);
    Ok(out)
}
