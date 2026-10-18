// Magic hexagon: arrange the numbers 1 to NUM_CELLS in the 19 cells A..S of a
// hexagon so that each of the 15 lines (rows and diagonals) sums to MAGIC_SUM.
// The cells are indexed A=0, B=1, ..., S=18 in reading order of the layout:
//   row 0: A B C; row 1: D E F G; row 2: H I J K L; row 3: M N O P; row 4: Q R S.
// The output LD lists the values of A..S in that order.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("NUM_CELLS");
    let magic = inst.int("MAGIC_SUM");

    // Every cell takes a distinct value from 1 to NUM_CELLS.
    let cells = m.new_int_decisions(n, 1..=(n as i64));
    m.unique(cells.clone()).post()?;

    // The three rows of the hexagon in each direction, of lengths 3, 4, 5, 4, 3.
    // Horizontal rows.
    // The line through A, B, C.
    // The line through D, E, F, G.
    // The line through H, I, J, K, L.
    // The line through M, N, O, P.
    // The line through Q, R, S.
    let horizontal: [&[usize]; 5] = [
        &[0, 1, 2],
        &[3, 4, 5, 6],
        &[7, 8, 9, 10, 11],
        &[12, 13, 14, 15],
        &[16, 17, 18],
    ];
    // Lines sloping one way across the hexagon.
    // The line through A, D, H.
    // The line through B, E, I, M.
    // The line through C, F, J, N, Q.
    // The line through G, K, O, R.
    // The line through L, P, S.
    let slope_down: [&[usize]; 5] = [
        &[0, 3, 7],
        &[1, 4, 8, 12],
        &[2, 5, 9, 13, 16],
        &[6, 10, 14, 17],
        &[11, 15, 18],
    ];
    // Lines sloping the other way across the hexagon.
    // The line through A, E, J, O, S.
    // The line through B, F, K, P.
    // The line through C, G, L.
    // The line through D, I, N, R.
    // The line through H, M, Q.
    let slope_up: [&[usize]; 5] = [
        &[0, 4, 9, 14, 18],
        &[1, 5, 10, 15],
        &[2, 6, 11],
        &[3, 8, 13, 17],
        &[7, 12, 16],
    ];

    // Each of the 15 lines sums to the magic constant.
    for line in horizontal.iter().chain(slope_down.iter()).chain(slope_up.iter()) {
        let vars: Vec<View<i64>> = line.iter().map(|&i| cells[i]).collect();
        m.linear(vars.iter().copied().sum::<IntLinearExp>()).eq(magic).post()?;
    }

    let mut out = Out::new();
    out.put("LD", cells);
    Ok(out)
}
