// Flow Free: colour the board with one colour per pair of matching endpoints,
// so that each colour forms a single pipe from its one endpoint to its other,
// covering every cell, with no two pipes sharing a cell.
// Colours are 1..=K, K the largest value on the board. Clue cells keep their colour.

// Neighbours of a cell (up, down, left, right) inside the board.
fn neighbours(cell: usize, rows: usize, cols: usize) -> Vec<usize> {
    let (r, c) = (cell / cols, cell % cols);
    let mut out = Vec::new();
    if r > 0 {
        out.push(cell - cols);
    }
    if r + 1 < rows {
        out.push(cell + cols);
    }
    if c > 0 {
        out.push(cell - 1);
    }
    if c + 1 < cols {
        out.push(cell + 1);
    }
    out
}

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let board = inst.matrix("board");
    let rows = board.len();
    let cols = board[0].len();
    let cells = rows * cols;
    let k_max = board.iter().flatten().copied().max().unwrap_or(1);

    // Colour of each cell. Clue cells are fixed to their value.
    // Each cell gets exactly one colour in 1..=K.
    let mut b: Vec<Vec<View<i64>>> = Vec::new();
    for r in 0..rows {
        let mut row = Vec::new();
        for c in 0..cols {
            let v = m.new_int_decision(1..=k_max);
            if board[r][c] != 0 {
                m.linear(v).eq(board[r][c]).post()?;
            }
            row.push(v);
        }
        b.push(row);
    }

    // is_col[ki][cell]: the cell has colour ki+1.
    let mut is_col: Vec<Vec<View<bool>>> = Vec::new();
    for k in 1..=k_max {
        let mut row = Vec::new();
        for cell in 0..cells {
            let (r, c) = (cell / cols, cell % cols);
            row.push(m.linear(b[r][c]).eq(k).reify());
        }
        is_col.push(row);
    }

    for k in 1..=k_max {
        let ki = (k - 1) as usize;
        let x = is_col[ki].clone();

        // The two clue cells of this colour, the first is the start of the pipe.
        let ends: Vec<usize> = (0..cells)
            .filter(|&cell| board[cell / cols][cell % cols] == k)
            .collect();
        if ends.len() != 2 {
            panic!("colour {k} has {} clue cells, expected 2", ends.len());
        }
        let start = ends[0];

        // Rank along the pipe: the start has rank 0, every other cell of this
        // colour has a predecessor one rank lower. Ranks strictly decrease
        // towards the start, so no cycle can form apart from the pipe.
        let mut rank = Vec::with_capacity(cells);
        for _ in 0..cells {
            rank.push(m.new_int_decision(0..=(cells as i64) - 1));
        }

        for cell in 0..cells {
            let nb = neighbours(cell, rows, cols);

            // A pipe cell has two same-colour neighbours, and an endpoint has one.
            let same: Vec<View<bool>> = nb.iter().map(|&u| x[u]).collect();
            let deg = same.iter().copied().sum::<IntLinearExp>();
            if cell == ends[0] || cell == ends[1] {
                m.linear(deg).eq(1).post()?;
            } else {
                m.linear(deg).eq(2).implied_by(x[cell]).post()?;
            }

            // The start of the pipe has rank 0.
            if cell == start {
                m.linear(rank[cell]).eq(0).post()?;
                continue;
            }

            // Every other cell of this colour needs a predecessor neighbour
            // of this colour with rank one lower.
            let mut preds = Vec::new();
            for &u in &nb {
                let p = m.new_bool_decision();
                m.linear(rank[cell] - rank[u]).eq(1).implied_by(p).post()?;
                m.linear(std::iter::once(x[u]).sum::<IntLinearExp>()).ge(1).implied_by(p).post()?;
                m.linear(std::iter::once(x[cell]).sum::<IntLinearExp>()).ge(1).implied_by(p).post()?;
                preds.push(p);
            }
            m.linear(preds.iter().copied().sum::<IntLinearExp>())
                .ge(1)
                .implied_by(x[cell])
                .post()?;
        }
    }

    let mut out = Out::new();
    out.put("B", b);
    Ok(out)
}
