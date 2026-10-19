// Magic square (session1_magic_square): an n x n grid (n != 2) where each cell
// holds a different integer from 1 to n^2 and every row, column and diagonal
// sums to n(n^2+1)/2. The size n comes from the instance.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let nn = (n * n) as i64;
    let target = (n as i64) * (nn + 1) / 2;

    // Each cell of the grid is an integer from 1 to n^2.
    let mut sq: Vec<Vec<View<i64>>> = Vec::with_capacity(n);
    for _ in 0..n {
        let mut row = Vec::with_capacity(n);
        for _ in 0..n {
            row.push(m.new_int_decision(1..=nn));
        }
        sq.push(row);
    }

    // Each cell contains a different integer.
    let all: Vec<View<i64>> = sq.iter().flatten().copied().collect();
    m.unique(all).post()?;

    // Each row sums to n(n^2+1)/2.
    for row in &sq {
        m.linear(row.iter().copied().sum::<IntLinearExp>()).eq(target).post()?;
    }

    // Each column sums to n(n^2+1)/2.
    for c in 0..n {
        m.linear(sq.iter().map(|r| r[c]).sum::<IntLinearExp>()).eq(target).post()?;
    }

    // Each diagonal sums to n(n^2+1)/2.
    m.linear((0..n).map(|i| sq[i][i]).sum::<IntLinearExp>()).eq(target).post()?;
    m.linear((0..n).map(|i| sq[i][n - 1 - i]).sum::<IntLinearExp>()).eq(target).post()?;

    let mut out = Out::new();
    out.put("square", sq);
    Ok(out)
}
