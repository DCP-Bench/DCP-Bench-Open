// Nonogram: shade cells of a grid so that every row and column shows the given
// blocks of consecutive shaded cells, in order, separated by at least one blank.

// One line of the grid must read as its rule. Pumpkin has no regular
// constraint, so the line is run through the automaton of its rule, spelled out
// as one state variable per position and one table constraint per step.
// Rule entries equal to 0 are padding and are ignored, as in the reference.
fn post_line_rule(solver: &mut Solver, line: &[Var], rule: &[i32]) {
    // The automaton: for each block, loop on blank cells before it, then step
    // through its shaded cells, then take one blank cell that closes the block.
    // The last state loops on blanks, so the line may end in a blank or in a block.
    let mut steps: Vec<Vec<i32>> = Vec::new(); // (state, cell value, next state)
    let mut n_states: i32 = 0;
    for &block in rule.iter().filter(|&&b| b != 0) {
        steps.push(vec![n_states, 0, n_states]);
        for _ in 0..block {
            steps.push(vec![n_states, 1, n_states + 1]);
            n_states += 1;
        }
        steps.push(vec![n_states, 0, n_states + 1]);
        n_states += 1;
    }
    steps.push(vec![n_states, 0, n_states]);

    // state[j] is the automaton state after reading the first j cells.
    // It starts in state 0 and must end in one of the last two states (the
    // second last when the line ends on a shaded cell); with no blocks at all
    // the only state, 0, accepts.
    let length = line.len();
    let state: Vec<Var> = (0..=length)
        .map(|j| {
            if j == 0 {
                solver.new_bounded_integer(0, 0)
            } else if j == length {
                solver.new_bounded_integer((n_states - 1).max(0), n_states)
            } else {
                solver.new_bounded_integer(0, n_states)
            }
        })
        .collect();
    let tag = solver.new_constraint_tag();
    for j in 0..length {
        solver
            .add_constraint(pumpkin_solver::table(
                vec![state[j], line[j], state[j + 1]], steps.clone(), tag))
            .post();
    }
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n_rows = inst.size("rows");
    let n_cols = inst.size("cols");
    let row_rules = inst.matrix("row_rules"); // blocks of each row, left to right
    let col_rules = inst.matrix("col_rules"); // blocks of each column, top to bottom

    // board[r][c] is 1 for a shaded cell and 0 for a blank one.
    let board: Vec<Vec<Var>> = (0..n_rows)
        .map(|_| (0..n_cols).map(|_| solver.new_bounded_integer(0, 1)).collect())
        .collect();

    // The pattern of each row must be its rule.
    for r in 0..n_rows {
        post_line_rule(solver, &board[r], &row_rules[r]);
    }
    // The pattern of each column must be its rule.
    for c in 0..n_cols {
        let column: Vec<Var> = (0..n_rows).map(|r| board[r][c]).collect();
        post_line_rule(solver, &column, &col_rules[c]);
    }

    let mut m = Model::new();
    m.put("board", board);
    m
}
