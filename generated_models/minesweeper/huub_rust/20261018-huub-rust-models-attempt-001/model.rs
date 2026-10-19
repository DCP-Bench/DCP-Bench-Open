// Minesweeper: determine which unopened ('X') cells of the board contain mines,
// from the numerical clues of the opened cells. game_data uses -1 for an unopened
// cell and a value >= 0 for an opened cell.
fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let board = inst.matrix("game_data");
    let rows = board.len();
    let cols = board[0].len();

    // mines[r][c] is true when the cell at row r, column c contains a mine.
    let mut mines: Vec<Vec<View<bool>>> = Vec::with_capacity(rows);
    for _ in 0..rows {
        let row: Vec<View<bool>> = (0..cols).map(|_| m.new_bool_decision()).collect();
        mines.push(row);
    }

    // Opened cells are safe: they cannot contain a mine.
    for r in 0..rows {
        for c in 0..cols {
            if board[r][c] >= 0 {
                m.linear(std::iter::once(mines[r][c]).sum::<IntLinearExp>())
                    .eq(0)
                    .post()?;
            }
        }
    }

    // The number on a cell shows the number of mines adjacent to it.
    for r in 0..rows {
        for c in 0..cols {
            let clue = board[r][c];
            if clue < 0 {
                continue;
            }
            let mut neighbours: Vec<View<bool>> = Vec::new();
            for dr in -1i64..=1 {
                for dc in -1i64..=1 {
                    if dr == 0 && dc == 0 {
                        continue;
                    }
                    let nr = r as i64 + dr;
                    let nc = c as i64 + dc;
                    if nr < 0 || nc < 0 || nr >= rows as i64 || nc >= cols as i64 {
                        continue;
                    }
                    neighbours.push(mines[nr as usize][nc as usize]);
                }
            }
            m.linear(neighbours.iter().copied().sum::<IntLinearExp>())
                .eq(clue)
                .post()?;
        }
    }

    let mut out = Out::new();
    out.put("mines", mines);
    Ok(out)
}
