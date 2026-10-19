// Schur's lemma (csplib 015): put the balls 1..n into c boxes so that for every
// triple of balls (x, y, z) with x + y = z, not all three are in the same box.
// Output: balls[i] (for ball i+1) is the box number, 1..c.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let c = inst.int("c");

    // Each ball gets one box, as an integer variable over 1..=c.
    // Its equality literals m[i][j] say ball i+1 is in box j+1.
    let balls: Vec<IntVar> = (0..n).map(|_| IntVar::new(1..=c)).collect();
    let mut m: Vec<Vec<Lit>> = Vec::with_capacity(n);
    for ball in &balls {
        let mut row = Vec::with_capacity(c as usize);
        for j in 1..=c {
            let b = ball.equals(s, j)?;
            row.push(lit_of(s, b)?);
        }
        m.push(row);
    }

    // For each x + y = z with x, y, z in 1..n (x <= y), and each box j,
    // the three balls are not all in box j.
    // When x = y, the triple has only two distinct balls: x and z.
    for x in 1..=n {
        for y in x..=n {
            let z = x + y;
            if z > n {
                break;
            }
            for j in 0..c as usize {
                let clause = if x == y {
                    vec![!m[x - 1][j], !m[z - 1][j]]
                } else {
                    vec![!m[x - 1][j], !m[y - 1][j], !m[z - 1][j]]
                };
                s.add_clause(clause)?;
            }
        }
    }

    let mut out = Out::new();
    out.put("balls", &balls);
    Ok(out)
}
