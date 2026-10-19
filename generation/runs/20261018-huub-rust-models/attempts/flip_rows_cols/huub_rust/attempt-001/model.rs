// Problem flip_rows_cols: given an array of positive and negative numbers, flip the
// sign of entire rows and columns (as many as you like) so that every row and every
// column sums to a positive number or zero. Among such solutions, minimise the overall
// sum of the array. Output row_signs and col_signs as lists of -1/1.
//
// Model: r[i] and c[j] are 0/1 flip decisions for row i and column j (1 = flipped).
// The cell (i,j) is negated exactly when f[i][j] = r[i] xor c[j] is 1, so the cell
// value is a[i][j] * (1 - 2 f[i][j]).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let a = inst.matrix("input_matrix");
    let rows = a.len();
    let cols = a[0].len();

    // Flip decisions for every row and every column.
    let mut r: Vec<View<i64>> = Vec::new();
    for _ in 0..rows {
        r.push(m.new_int_decision(0..=1));
    }
    let mut c: Vec<View<i64>> = Vec::new();
    for _ in 0..cols {
        c.push(m.new_int_decision(0..=1));
    }

    // Output signs: sign = 1 - 2 * flip.
    let mut row_signs: Vec<View<i64>> = Vec::new();
    for i in 0..rows {
        let s = m.new_int_decision(-1..=1);
        m.linear(s + r[i] * 2).eq(1).post()?;
        row_signs.push(s);
    }
    let mut col_signs: Vec<View<i64>> = Vec::new();
    for j in 0..cols {
        let s = m.new_int_decision(-1..=1);
        m.linear(s + c[j] * 2).eq(1).post()?;
        col_signs.push(s);
    }

    // Parity of each cell: f[i][j] = r[i] xor c[j], written as linear inequalities
    // that hold exactly for 0/1 values.
    let mut f: Vec<Vec<View<i64>>> = Vec::new();
    for i in 0..rows {
        let mut line: Vec<View<i64>> = Vec::new();
        for j in 0..cols {
            let x = m.new_int_decision(0..=1);
            m.linear(x - r[i] - c[j]).le(0).post()?;
            m.linear(x - r[i] + c[j]).ge(0).post()?;
            m.linear(x + r[i] - c[j]).ge(0).post()?;
            m.linear(x + r[i] + c[j]).le(2).post()?;
            line.push(x);
        }
        f.push(line);
    }

    // The value of cell (i,j) after the flips is a[i][j] - 2 a[i][j] f[i][j].
    // Each row, after the flips, sums to a positive number or zero:
    // sum_j a[i][j] (1 - 2 f[i][j]) >= 0.
    for i in 0..rows {
        let rowsum: i64 = a[i].iter().sum();
        let mut terms: Vec<_> = Vec::new();
        for j in 0..cols {
            terms.push(f[i][j] * (-2 * a[i][j]));
        }
        let mut it = terms.into_iter();
        let mut e = IntLinearExp::from(it.next().unwrap());
        for t in it {
            e = e + t;
        }
        m.linear(e).ge(-rowsum).post()?;
    }

    // Each column, after the flips, sums to a positive number or zero:
    // sum_i a[i][j] (1 - 2 f[i][j]) >= 0.
    for j in 0..cols {
        let colsum: i64 = (0..rows).map(|i| a[i][j]).sum();
        let mut terms: Vec<_> = Vec::new();
        for i in 0..rows {
            terms.push(f[i][j] * (-2 * a[i][j]));
        }
        let mut it = terms.into_iter();
        let mut e = IntLinearExp::from(it.next().unwrap());
        for t in it {
            e = e + t;
        }
        m.linear(e).ge(-colsum).post()?;
    }

    // The objective is the overall sum of the flipped array, to be minimised:
    // sum_ij a[i][j] (1 - 2 f[i][j]) = obj.
    let total: i64 = a.iter().flatten().sum();
    let bound: i64 = a.iter().flatten().map(|v| v.abs()).sum();
    let mut terms: Vec<_> = Vec::new();
    for i in 0..rows {
        for j in 0..cols {
            terms.push(f[i][j] * (-2 * a[i][j]));
        }
    }
    let mut it = terms.into_iter();
    let mut e = IntLinearExp::from(it.next().unwrap());
    for t in it {
        e = e + t;
    }
    let obj = m.new_int_decision(-bound..=bound);
    m.linear(e - obj).eq(-total).post()?;

    let mut out = Out::new();
    out.put("row_signs", row_signs).put("col_signs", col_signs);
    out.minimise(obj);
    Ok(out)
}
