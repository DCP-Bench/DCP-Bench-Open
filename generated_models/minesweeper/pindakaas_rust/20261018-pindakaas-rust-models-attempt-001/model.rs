// Minesweeper: the board is a grid of cells. Cells with a number are opened and
// hold no mine; the number is the count of mines among the eight cells around it.
// Output mines[i][j] is true where a mine sits. Cells marked -1 are unopened and
// their mine status is left to the clues.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let game = inst.matrix("game_data");
    let rows = game.len();
    let cols = game[0].len();

    // One mine literal per cell of this instance's board.
    let mut mines: Vec<Vec<Lit>> = Vec::with_capacity(rows);
    for _ in 0..rows {
        let mut row = Vec::with_capacity(cols);
        for _ in 0..cols {
            row.push(s.new_lit());
        }
        mines.push(row);
    }

    // An opened cell with a number is not a mine.
    // (A cell marked -1 is unopened and may or may not be a mine.)
    for i in 0..rows {
        for j in 0..cols {
            if game[i][j] >= 0 {
                s.add_clause([!mines[i][j].clone()])?;
            }
        }
    }

    // Each number on an opened cell is the count of mines in the eight cells around it.
    for i in 0..rows {
        for j in 0..cols {
            let clue = game[i][j];
            if clue < 0 {
                continue;
            }
            let mut around = LinExp::default();
            for di in -1i64..=1 {
                for dj in -1i64..=1 {
                    if di == 0 && dj == 0 {
                        continue;
                    }
                    let (a, b) = (i as i64 + di, j as i64 + dj);
                    if a < 0 || b < 0 || a >= rows as i64 || b >= cols as i64 {
                        continue;
                    }
                    around += LinExp::from(mines[a as usize][b as usize].clone());
                }
            }
            post(s, around, Comparator::Equal, clue)?;
        }
    }

    let mut out = Out::new();
    out.put("mines", &mines);
    Ok(out)
}
