// KenKen on an n x n grid (n from the instance): fill the grid with the digits 1..n
// so that each row and each column contains every digit exactly once. Each cage is a
// group of cells with a target value that the cells satisfy under one operation. The
// instance does not name the operation, so a cage admits any operation that fits its size:
// a single cell holds its target; a two-cell cage holds its target under sum, difference,
// product or exact quotient; a larger cage under sum or product. Digits may repeat in a cage.

// Every assignment of the cage cells (values 1..=n) that satisfies the cage.
fn cage_tuples(target: i64, k: usize, n: i64) -> Vec<Vec<i64>> {
    let mut rows = Vec::new();
    let total = n.pow(k as u32);
    for idx in 0..total {
        let mut rem = idx;
        let mut cur = vec![0i64; k];
        for j in 0..k {
            cur[j] = rem % n + 1;
            rem /= n;
        }
        let sum: i64 = cur.iter().sum();
        let prod: i64 = cur.iter().product();
        let ok = if k == 2 {
            let (a, b) = (cur[0], cur[1]);
            a + b == target
                || a * b == target
                || (a - b).abs() == target
                || a == target * b
                || b == target * a
        } else {
            sum == target || prod == target
        };
        if ok {
            rows.push(cur);
        }
    }
    rows
}

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");

    // The grid: x[r][c] in 1..=n.
    let mut x: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..n {
        let mut row = Vec::new();
        for _ in 0..n {
            row.push(m.new_int_decision(1..=n));
        }
        x.push(row);
    }

    // Each row contains every digit once.
    for r in 0..n as usize {
        m.unique(x[r].clone()).post()?;
    }

    // Each column contains every digit once.
    for c in 0..n as usize {
        let col: Vec<View<i64>> = (0..n as usize).map(|r| x[r][c]).collect();
        m.unique(col).post()?;
    }

    // Cages: a list of [target, [[row, col], ...]] with 1-based coordinates.
    let cages = inst
        .get("problem")
        .as_array()
        .expect("problem is a list of cages");
    for cage in cages {
        let target = cage[0].as_i64().expect("cage target is an integer");
        let cells = cage[1].as_array().expect("cage cells are a list");
        let vars: Vec<View<i64>> = cells
            .iter()
            .map(|cell| {
                let r = cell[0].as_i64().expect("row is an integer") as usize;
                let c = cell[1].as_i64().expect("column is an integer") as usize;
                x[r - 1][c - 1]
            })
            .collect();

        // A cage of one cell is its target. Larger cages are a table of the
        // tuples that satisfy the cage's operation.
        if vars.len() == 1 {
            m.linear(vars[0]).eq(target).post()?;
        } else {
            let rows = cage_tuples(target, vars.len(), n);
            m.table(vars).values(rows).post()?;
        }
    }

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
