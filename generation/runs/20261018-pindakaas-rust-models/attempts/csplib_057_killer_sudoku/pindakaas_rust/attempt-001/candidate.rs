// Killer sudoku: a 9x9 grid (size n from the instance) filled with the numbers 1 to 9.
// The cages are the instance field `problem`: each entry is [sum, [[row, col], ...]] with
// 1-based coordinates.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let b = (1..=n).find(|k| k * k == n).expect("the grid is a square of nonets");
    let top = n as i64;

    let x: Vec<Vec<IntVar>> = (0..n)
        .map(|_| (0..n).map(|_| IntVar::new(1..=top)).collect())
        .collect();

    // Each row, column, and nonet contains each number exactly once.
    for i in 0..n {
        all_different(s, &x[i])?;
    }
    for j in 0..n {
        let col: Vec<IntVar> = (0..n).map(|i| x[i][j].clone()).collect();
        all_different(s, &col)?;
    }
    for br in 0..n / b {
        for bc in 0..n / b {
            let mut nonet = Vec::new();
            for i in 0..b {
                for j in 0..b {
                    nonet.push(x[br * b + i][bc * b + j].clone());
                }
            }
            all_different(s, &nonet)?;
        }
    }

    let cages = inst.get("problem").as_array().expect("problem is a list of cages");
    for cage in cages {
        let parts = cage.as_array().expect("a cage is [sum, cells]");
        let sum = parts[0].as_i64().expect("the cage sum is an integer");
        let cells: Vec<IntVar> = parts[1]
            .as_array()
            .expect("the cage cells are a list")
            .iter()
            .map(|p| {
                let rc = p.as_array().expect("a cell is [row, col]");
                let r = rc[0].as_i64().expect("row") as usize - 1;
                let c = rc[1].as_i64().expect("col") as usize - 1;
                x[r][c].clone()
            })
            .collect();

        // The sum of all numbers in a cage must match the small number printed in its corner.
        let mut e = LinExp::default();
        for v in &cells {
            e += iv(v);
        }
        post(s, e, Comparator::Equal, sum)?;

        // No number appears more than once in a cage.
        all_different(s, &cells)?;
    }

    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
