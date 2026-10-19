// CSPLib 067, quasigroup completion: complete a partially filled order N
// quasigroup. An order N quasigroup is an N x N Latin square with the
// symbols 1 to N, each occurring exactly once in every row and every column.
// The given cells of start (nonzero entries) keep their values; 0 marks an
// empty cell. The output puzzle is the completed square.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("N");
    let m = n as i64;
    let start = inst.matrix("start");

    // Each cell of the square takes a symbol from 1 to N.
    let puzzle: Vec<Vec<IntVar>> = (0..n)
        .map(|_| (0..n).map(|_| IntVar::new(1..=m)).collect())
        .collect();

    // The given cells keep their values.
    // Nonzero entries of the start square are fixed in the completed square.
    for i in 0..n {
        for j in 0..n {
            let v = start[i][j];
            if v != 0 {
                post(s, iv(&puzzle[i][j]), Comparator::Equal, v)?;
            }
        }
    }

    // Every row of the square contains each symbol from 1 to N exactly once.
    for i in 0..n {
        all_different(s, &puzzle[i])?;
    }

    // Every column of the square contains each symbol from 1 to N exactly once.
    for j in 0..n {
        let col: Vec<IntVar> = (0..n).map(|i| puzzle[i][j].clone()).collect();
        all_different(s, &col)?;
    }

    let mut out = Out::new();
    out.put("puzzle", &puzzle);
    Ok(out)
}
