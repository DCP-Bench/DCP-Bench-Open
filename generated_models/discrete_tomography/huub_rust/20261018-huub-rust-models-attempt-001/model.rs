// Discrete tomography: a matrix of 0s and 1s is x-rayed by its row sums and
// its column sums. Reconstruct the matrix from these counts.
// The matrix has one row per entry of row_sums and one column per entry of
// col_sums, so the dimensions come from each instance.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let row_sums = inst.ints("row_sums");
    let col_sums = inst.ints("col_sums");
    let rows = row_sums.len();
    let cols = col_sums.len();

    // The matrix contains zeroes and ones.
    let mut cell: Vec<Vec<View<i64>>> = Vec::with_capacity(rows);
    for _ in 0..rows {
        let mut line: Vec<View<i64>> = Vec::with_capacity(cols);
        for _ in 0..cols {
            line.push(m.new_int_decision(0..=1));
        }
        cell.push(line);
    }

    // The number of ones in each row is the row's x-ray count.
    for i in 0..rows {
        let total: IntLinearExp = cell[i].iter().copied().sum();
        m.linear(total).eq(row_sums[i]).post()?;
    }

    // The number of ones in each column is the column's x-ray count.
    for j in 0..cols {
        let total: IntLinearExp = (0..rows).map(|i| cell[i][j]).sum();
        m.linear(total).eq(col_sums[j]).post()?;
    }

    let mut out = Out::new();
    out.put("matrix", cell);
    Ok(out)
}
