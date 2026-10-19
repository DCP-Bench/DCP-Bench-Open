// Schur's lemma (CSPLib 015): put the balls 1, ..., n into c boxes so that for any
// triple of balls (x, y, z) with x + y = z, not all three are in the same box.
// Each ball gets one box number from 1 to c. Sizes n and c come from the instance.

// Constraint: for every triple (x, y, z) with x + y = z, not all three balls in the same box.
// Triples range over the balls 1..=n; x = y is included.
fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let c = inst.int("c");

    // Constraint: each ball is in exactly one box, numbered 1..=c.
    let balls: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(1..=c)).collect();

    // in_box[i][j] is true exactly when ball i + 1 is in box j + 1.
    let mut in_box: Vec<Vec<View<bool>>> = Vec::with_capacity(n);
    for i in 0..n {
        let mut row: Vec<View<bool>> = Vec::with_capacity(c as usize);
        for j in 1..=c {
            row.push(m.linear(balls[i]).eq(j).reify());
        }
        in_box.push(row);
    }

    // Constraint: for each triple x + y = z and each box j, at most two of the three balls are in box j.
    for x in 1..=n {
        for y in x..=n {
            let z = x + y;
            if z > n {
                break;
            }
            for j in 0..c as usize {
                let bx = in_box[x - 1][j];
                let by = in_box[y - 1][j];
                let bz = in_box[z - 1][j];
                m.linear([bx, by, bz].into_iter().sum::<IntLinearExp>()).le(2).post()?;
            }
        }
    }

    let mut out = Out::new();
    out.put("balls", balls);
    Ok(out)
}
