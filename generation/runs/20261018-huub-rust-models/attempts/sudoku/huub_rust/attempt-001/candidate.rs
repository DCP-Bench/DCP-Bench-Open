// Sudoku: fill a 9x9 grid with the digits 1 to 9 so that each row, each column
// and each 3x3 section contains all the digits. The input grid gives some cells
// as numbers and leaves the others empty (0). Output the solved grid as grid.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let given = inst.matrix("input_grid");

    // Each cell holds a digit between 1 and 9.
    let mut grid: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..9 {
        let row: Vec<View<i64>> = (0..9).map(|_| m.new_int_decision(1..=9)).collect();
        grid.push(row);
    }

    // The digits given in the input stay fixed.
    // Cells that are empty in the input (0) are left free.
    for i in 0..9 {
        for j in 0..9 {
            let v = given[i][j];
            if v != 0 {
                m.linear(grid[i][j]).eq(v).post()?;
            }
        }
    }

    // Each row contains all the digits between 1 and 9.
    for i in 0..9 {
        m.unique(grid[i].clone()).post()?;
    }

    // Each column contains all the digits between 1 and 9.
    for j in 0..9 {
        let col: Vec<View<i64>> = (0..9).map(|i| grid[i][j]).collect();
        m.unique(col).post()?;
    }

    // Each 3x3 section contains all the digits between 1 and 9.
    for bi in 0..3 {
        for bj in 0..3 {
            let mut section: Vec<View<i64>> = Vec::new();
            for di in 0..3 {
                for dj in 0..3 {
                    section.push(grid[bi * 3 + di][bj * 3 + dj]);
                }
            }
            m.unique(section).post()?;
        }
    }

    let mut out = Out::new();
    out.put("grid", grid);
    Ok(out)
}
