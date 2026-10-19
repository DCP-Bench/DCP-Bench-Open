// Kakuro: fill each white cell of an n x n grid with a digit from 1 to 9.
// Each entry (a clue and the cells it covers) must sum to its clue, and no digit
// may be duplicated within an entry. Output x holds the digits; 0 marks black and clue cells.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");

    // The listed blanks (1-based row, column) are black cells, not white. Every other cell is white.
    let mut white = vec![vec![true; n]; n];
    for b in inst.matrix("blanks") {
        white[(b[0] - 1) as usize][(b[1] - 1) as usize] = false;
    }

    // Digit in each white cell, 1 to 9.
    let mut x: Vec<Vec<View<i64>>> = Vec::with_capacity(n);
    for r in 0..n {
        let mut row = Vec::with_capacity(n);
        for c in 0..n {
            let cell = if white[r][c] {
                m.new_int_decision(1..=9)
            } else {
                m.new_int_decision(0..=0)
            };
            row.push(cell);
        }
        x.push(row);
    }

    // Each entry of the problem is [clue, [row, col], [row, col], ...] (1-based cells).
    let entries = inst.get("problem").as_array().expect("problem is an array");
    for entry in entries {
        let parts = entry.as_array().expect("entry is an array");
        let clue = parts[0].as_i64().expect("clue is an integer");
        let cells: Vec<View<i64>> = parts[1..]
            .iter()
            .map(|p| {
                let rc = p.as_array().expect("cell is an array");
                let r = (rc[0].as_i64().expect("row") - 1) as usize;
                let c = (rc[1].as_i64().expect("column") - 1) as usize;
                x[r][c]
            })
            .collect();

        // The digits of an entry sum to its clue.
        eq2(m, cells.iter().copied().sum::<IntLinearExp>(), clue)?;

        // No digit is duplicated within an entry.
        m.unique(cells.clone()).post()?;
    }

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
