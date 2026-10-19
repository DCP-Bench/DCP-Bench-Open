// Magic square of size n (n != 2): an n x n grid of distinct integers 1..n^2
// such that the sum of each row, column and diagonal is n(n^2+1)/2.
// Output: square, an n x n list of lists of integers.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let nn = (n * n) as i64;
    let target = (n as i64) * (nn + 1) / 2;

    // The description: each cell contains a different integer from 1 to n^2.
    let grid: Vec<Vec<IntVar>> = (0..n)
        .map(|_| (0..n).map(|_| IntVar::new(1..=nn)).collect())
        .collect();
    let flat: Vec<IntVar> = grid.iter().flat_map(|row| row.iter().cloned()).collect();
    all_different(s, &flat)?;

    // The description: the sum of the integers in each row, column and diagonal is equal
    // to n(n^2+1)/2.
    for row in &grid {
        let e = row.iter().fold(LinExp::default(), |acc, x| acc + iv(x));
        post(s, e, Comparator::Equal, target)?;
    }
    for c in 0..n {
        let e = (0..n).fold(LinExp::default(), |acc, r| acc + iv(&grid[r][c]));
        post(s, e, Comparator::Equal, target)?;
    }
    let diag = (0..n).fold(LinExp::default(), |acc, i| acc + iv(&grid[i][i]));
    post(s, diag, Comparator::Equal, target)?;
    let anti = (0..n).fold(LinExp::default(), |acc, i| acc + iv(&grid[i][n - 1 - i]));
    post(s, anti, Comparator::Equal, target)?;

    let mut out = Out::new();
    out.put("square", &grid);
    Ok(out)
}
