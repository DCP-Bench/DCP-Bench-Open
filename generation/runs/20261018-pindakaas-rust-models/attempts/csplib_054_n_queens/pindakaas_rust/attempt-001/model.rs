// Problem: csplib_054_n_queens. Can n queens be placed on an n x n chessboard so that
// no two queens attack each other? Queens attack along the same row, column or diagonal.
// queens[i] is the column (1..n) of the queen in row i.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    // The i-th integer is the column position of the queen in the i-th row.
    let queens: Vec<IntVar> = (0..n).map(|_| IntVar::new(1..=n)).collect();

    // no two queens of the same column: the queens occupy distinct columns.
    all_different(s, &queens)?;

    // no two queens of the same diagonal: queens[i] + i and queens[i] - i are each pairwise distinct.
    let mut ups: Vec<IntVar> = Vec::new();
    let mut downs: Vec<IntVar> = Vec::new();
    for i in 0..n {
        let u = IntVar::new(1 + i..=n + i);
        post(s, iv(&queens[i as usize]) - iv(&u), Comparator::Equal, -i)?;
        ups.push(u);
        let d = IntVar::new(1 - i..=n - i);
        post(s, iv(&queens[i as usize]) - iv(&d), Comparator::Equal, i)?;
        downs.push(d);
    }
    all_different(s, &ups)?;
    all_different(s, &downs)?;

    let mut out = Out::new();
    out.put("queens", &queens);
    Ok(out)
}
