// csplib_054_n_queens: place n queens on an n x n board so that no two queens
// share a row, a column or a diagonal. queens[i] is the column of the queen in row i (1-based).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let ni = n as i64;

    // Can n queens (of the same color) be placed on a n x n chessboard so that none of the queens can attack
    // each other? A queen attacks other squares on the same row, column, or either diagonal as itself.
    // Print the positions of the queens on the chessboard (queens) as a list of n integers, ranging from 1 to n,
    // where the i-th integer represents the column position of the queen in the i-th row.
    let mut queens = Vec::with_capacity(n);
    for _ in 0..n {
        queens.push(m.new_int_decision(1..=ni));
    }

    // No two queens are in the same column.
    m.unique(queens.clone()).post()?;

    // No two queens are on the same diagonal: the values queens[i] + i are all different.
    // No two queens are on the same anti-diagonal: the values queens[i] - i are all different.
    let mut up = Vec::with_capacity(n);
    let mut down = Vec::with_capacity(n);
    for i in 0..n {
        let u = m.new_int_decision(1..=2 * ni - 1);
        let d = m.new_int_decision(1 - ni..=ni);
        let ii = i as i64;
        // u = queens[i] + i
        m.linear(queens[i] - u).eq(-ii).post()?;
        // d = queens[i] - i
        m.linear(queens[i] - d).eq(ii).post()?;
        up.push(u);
        down.push(d);
    }
    m.unique(up).post()?;
    m.unique(down).post()?;

    let mut out = Out::new();
    out.put("queens", queens);
    Ok(out)
}
