// Calvin puzzle: fill an n by n grid so that every square holds one of the
// numbers 1 to n^2, each number used once. The numbers are placed in order
// 1, 2, ..., n^2, and each step moves to the next square of the grid.
// n is read from the instance.

// Grid squares are numbered row by row, cell c = row * n + col, and the
// flat list `cells` holds the number in each square.
// Each number k has a position `pos[k - 1]`, the square it is placed in.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let nn = n * n;

    // Every square is filled, and each number from 1 to n^2 is used exactly once.
    let cells = m.new_int_decisions(nn, 1..=(nn as i64));
    m.unique(cells.clone()).post()?;

    // The position of number k is the square that holds k: cells[pos[k-1]] == k.
    let pos = m.new_int_decisions(nn, 0..=(nn as i64 - 1));
    for k in 1..=nn {
        let value = m.new_int_decision(k as i64..=k as i64);
        m.element(cells.clone())
            .index(pos[k - 1])
            .result(value)
            .post()?;
    }

    // Movement Type I: if the next number is placed vertically or horizontally,
    // it must be placed exactly three squares away from the previous number
    // (there must be a two square gap between the numbers).
    // Movement Type II: if the next number is placed diagonally, it must be
    // placed exactly two squares away from the previous number (there must be
    // a one square gap between the numbers).
    // The allowed square pairs are the same for every step, so they are listed once.
    let mut allowed: Vec<Vec<i64>> = Vec::new();
    for a in 0..nn {
        for b in 0..nn {
            let dr = ((b / n) as i64 - (a / n) as i64).abs();
            let dc = ((b % n) as i64 - (a % n) as i64).abs();
            let vertical_or_horizontal = (dr == 0 && dc == 3) || (dr == 3 && dc == 0);
            let diagonal = dr == 2 && dc == 2;
            if vertical_or_horizontal || diagonal {
                allowed.push(vec![a as i64, b as i64]);
            }
        }
    }
    for k in 0..nn - 1 {
        m.table(vec![pos[k], pos[k + 1]])
            .values(allowed.clone())
            .post()?;
    }

    let grid: Vec<Vec<View<i64>>> = (0..n)
        .map(|r| cells[r * n..(r + 1) * n].to_vec())
        .collect();
    let mut out = Out::new();
    out.put("x", grid);
    Ok(out)
}
