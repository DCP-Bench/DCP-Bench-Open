// Problem: heterosquare. An n*n square x of distinct integers from 1 to n^2
// such that the sums of the rows, columns and diagonals are all different.
// Output: x as a list of lists of integers.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let nn = (n * n) as i64;

    // A heterosquare of order n is a n*n square whose elements are distinct integers from 1 to n^2.
    let mut x: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..n {
        let mut row = Vec::new();
        for _ in 0..n {
            row.push(m.new_int_decision(1..=nn));
        }
        x.push(row);
    }
    let flat: Vec<View<i64>> = x.iter().flatten().cloned().collect();
    m.unique(flat).post()?;

    // The sums of the rows, columns and diagonals are all different.
    // Each line has n cells and every cell is at most n^2, so a sum is at most n^3.
    let mut lines: Vec<Vec<View<i64>>> = Vec::new();
    for i in 0..n {
        lines.push(x[i].clone());
    }
    for j in 0..n {
        lines.push((0..n).map(|i| x[i][j].clone()).collect());
    }
    lines.push((0..n).map(|i| x[i][i].clone()).collect());
    lines.push((0..n).map(|i| x[i][n - 1 - i].clone()).collect());

    let max_sum = (n as i64) * nn;
    let mut sums: Vec<View<i64>> = Vec::new();
    for line in lines {
        let s = m.new_int_decision(n as i64..=max_sum);
        m.linear(line.iter().cloned().sum::<IntLinearExp>()).eq(s).post()?;
        sums.push(s);
    }
    m.unique(sums).post()?;

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
