// csplib 012, nonogram: shade squares of a rows x cols grid (1 = shaded, 0 = unshaded)
// so that the blocks of consecutive shaded squares satisfy the constraints given for
// each row and each column. Output: the board as a list of lists of integers.

// The nonzero entries of a rule, in order. Zeros are padding and mean no block.
fn blocks_of(rule: &[i64]) -> Vec<i64> {
    rule.iter().copied().filter(|&b| b > 0).collect()
}

// Transition tuples (state, cell, next state) of an automaton that accepts exactly the
// 0/1 strings whose maximal runs of 1s are the given blocks, in order. A state (k, r)
// means k blocks have been started and r is the length of the current run of 1s
// (r = 0 when the last cell is 0). Returns the number of states, the tuples and the
// accepting states.
fn automaton(blocks: &[i64]) -> (i64, Vec<Vec<i64>>, Vec<i64>) {
    let b = blocks.len();
    let maxr = blocks.iter().copied().max().unwrap_or(0);
    let w = maxr + 1;
    let id = |k: usize, r: i64| (k as i64) * w + r;
    let nstates = (b as i64 + 1) * w;
    let mut tuples: Vec<Vec<i64>> = Vec::new();
    for k in 0..=b {
        for r in 0..=maxr {
            if k == 0 && r > 0 {
                continue;
            }
            let s = id(k, r);
            // A 0 cell: ends the current run, which must be complete, or continues a gap.
            if r == 0 {
                tuples.push(vec![s, 0, id(k, 0)]);
            } else if r == blocks[k - 1] {
                tuples.push(vec![s, 0, id(k, 0)]);
            }
            // A 1 cell: extends the current run within its block, or starts the next block.
            if r > 0 {
                if r < blocks[k - 1] {
                    tuples.push(vec![s, 1, id(k, r + 1)]);
                }
            } else if k < b {
                tuples.push(vec![s, 1, id(k + 1, 1)]);
            }
        }
    }
    let mut accept = vec![id(b, 0)];
    if b >= 1 && blocks[b - 1] > 0 {
        accept.push(id(b, blocks[b - 1]));
    }
    (nstates, tuples, accept)
}

// Posts that the cells of one line (a row or a column) read as the given blocks.
fn line(m: &mut Model, cells: &[View<i64>], blocks: &[i64]) -> Res<()> {
    let (ns, tuples, accept) = automaton(blocks);
    let st: Vec<View<i64>> = m.new_int_decisions(cells.len() + 1, 0..=(ns - 1));
    m.linear(st[0]).eq(0).post()?;
    for (j, c) in cells.iter().enumerate() {
        m.table(vec![st[j], *c, st[j + 1]])
            .values(tuples.clone())
            .post()?;
    }
    let last: Vec<Vec<i64>> = accept.iter().map(|&a| vec![a]).collect();
    m.table(vec![st[cells.len()]]).values(last).post()?;
    Ok(())
}

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let rows = inst.size("rows");
    let cols = inst.size("cols");
    let row_rules = inst.matrix("row_rules");
    let col_rules = inst.matrix("col_rules");

    let mut board: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..rows {
        board.push(m.new_int_decisions(cols, 0..=1));
    }

    // blocks of consecutive shaded squares satisfy the constraints given for each row
    for i in 0..rows {
        let blocks = blocks_of(&row_rules[i]);
        line(m, &board[i], &blocks)?;
    }

    // blocks of consecutive shaded squares satisfy the constraints given for each column
    for j in 0..cols {
        let cells: Vec<View<i64>> = (0..rows).map(|i| board[i][j]).collect();
        let blocks = blocks_of(&col_rules[j]);
        line(m, &cells, &blocks)?;
    }

    let mut out = Out::new();
    out.put("board", board);
    Ok(out)
}
