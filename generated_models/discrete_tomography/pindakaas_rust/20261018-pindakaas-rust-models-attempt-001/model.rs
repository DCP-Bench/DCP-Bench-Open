// Discrete tomography: a matrix of zeroes and ones is x-rayed vertically and
// horizontally, giving the total number of ones in each row and column.
// Reconstruct the contents of the matrix from these sums.
// Output: the matrix (0 and 1) as a list of lists.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let row_sums = inst.ints("row_sums");
    let col_sums = inst.ints("col_sums");
    let (nr, nc) = (row_sums.len(), col_sums.len());

    // The matrix has one row per row sum and one column per column sum.
    // Each cell contains zero or one.
    let mut x: Vec<Vec<IntVar>> = Vec::with_capacity(nr);
    for _ in 0..nr {
        let row: Vec<IntVar> = (0..nc).map(|_| IntVar::new(0..=1)).collect();
        x.push(row);
    }

    // The total number of ones in each row is the row sum.
    for i in 0..nr {
        let mut e = LinExp::default();
        for j in 0..nc {
            e += iv(&x[i][j]);
        }
        post(s, e, Comparator::Equal, row_sums[i])?;
    }

    // The total number of ones in each column is the column sum.
    for j in 0..nc {
        let mut e = LinExp::default();
        for i in 0..nr {
            e += iv(&x[i][j]);
        }
        post(s, e, Comparator::Equal, col_sums[j])?;
    }

    let mut out = Out::new();
    out.put("matrix", &x);
    Ok(out)
}
