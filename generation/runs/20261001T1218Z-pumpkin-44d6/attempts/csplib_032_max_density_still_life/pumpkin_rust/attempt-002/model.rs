// Maximum density still life (CSPLib 32): choose the live cells of an n x m
// region of Conway's Game of Life, with every cell outside it dead, so that the
// pattern does not change from one generation to the next, maximising the
// number of live cells.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let m = inst.size("m");

    // grid[i][j] is true when cell (i, j) is alive.
    let grid: Vec<Vec<Lit>> = (0..n)
        .map(|_| (0..m).map(|_| solver.new_literal()).collect())
        .collect();

    // The still-life rule as allowed (live neighbours, cell) pairs: a dead cell
    // (0) may have any number of live neighbours except exactly 3, and a live
    // cell (1) must have exactly 2 or 3.
    let mut rule: Vec<Vec<i32>> = (0..9).filter(|&k| k != 3).map(|k| vec![k, 0]).collect();
    rule.push(vec![2, 1]);
    rule.push(vec![3, 1]);

    // Every cell of the region obeys the rule. alive_around is the number of
    // live neighbours inside the region (outside cells are dead and add nothing).
    let counting = solver.new_constraint_tag();
    let still = solver.new_constraint_tag();
    for i in 0..n {
        for j in 0..m {
            let mut around: Vec<Lit> = Vec::new();
            for di in -1i32..=1 {
                for dj in -1i32..=1 {
                    let (a, b) = (i as i32 + di, j as i32 + dj);
                    if (di, dj) != (0, 0) && a >= 0 && b >= 0 && a < n as i32 && b < m as i32 {
                        around.push(grid[a as usize][b as usize]);
                    }
                }
            }
            let alive_around = solver.new_bounded_integer(0, around.len() as i32);
            if !around.is_empty() {
                solver
                    .add_constraint(pumpkin_solver::boolean_equals(
                        vec![1; around.len()], around, alive_around, counting))
                    .post();
            }
            let cell = grid[i][j].get_integer_variable();
            let alive_var = solver.new_bounded_integer(0, 1);
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![alive_var.scaled(1), cell.scaled(-1)], 0, counting))
                .post();
            solver
                .add_constraint(pumpkin_solver::table(vec![alive_around, alive_var], rule.clone(), still))
                .post();
        }
    }

    // The same rule stated a second time as clauses over the neighbour literals,
    // added because clause learning works directly on them: for a cell with
    // neighbour set N, a live cell has no 4 live neighbours and no 7 (or all but
    // one of N) dead ones, and a dead cell has no set of exactly 3 live
    // neighbours with the rest dead. Restates the table above; removes nothing.
    let rule_clauses = solver.new_constraint_tag();
    for i in 0..n {
        for j in 0..m {
            let mut around: Vec<Lit> = Vec::new();
            for di in -1i32..=1 {
                for dj in -1i32..=1 {
                    let (a, b) = (i as i32 + di, j as i32 + dj);
                    if (di, dj) != (0, 0) && a >= 0 && b >= 0 && a < n as i32 && b < m as i32 {
                        around.push(grid[a as usize][b as usize]);
                    }
                }
            }
            let cell = grid[i][j];
            let k = around.len();
            for mask in 0u32..(1u32 << k) {
                let ones = mask.count_ones() as usize;
                let chosen: Vec<Lit> = (0..k).filter(|&b| mask & (1 << b) != 0).map(|b| around[b]).collect();
                let rest: Vec<Lit> = (0..k).filter(|&b| mask & (1 << b) == 0).map(|b| around[b]).collect();
                if ones == 4 {
                    // live -> not all four of these alive
                    let mut c: Vec<Lit> = vec![!cell];
                    c.extend(chosen.iter().map(|&l| !l));
                    solver.add_constraint(pumpkin_solver::clause(c, rule_clauses)).post();
                }
                if ones + 1 == k || k < 2 && ones == 0 {
                    // live -> at least two of the neighbours alive: among any
                    // k - 1 of them at least one is alive
                    let mut c: Vec<Lit> = vec![!cell];
                    c.extend(chosen.iter().copied());
                    solver.add_constraint(pumpkin_solver::clause(c, rule_clauses)).post();
                }
                if ones == 3 {
                    // these three alive and the rest dead -> the cell is alive
                    let mut c: Vec<Lit> = vec![cell];
                    c.extend(chosen.iter().map(|&l| !l));
                    c.extend(rest.iter().copied());
                    solver.add_constraint(pumpkin_solver::clause(c, rule_clauses)).post();
                }
            }
        }
    }

    // Implied constraint, added to help prove the optimum: in a still life any
    // 3 x 3 square holds at most 6 live cells. This was checked by enumerating
    // every 5 x 5 pattern whose inner 3 x 3 cells all obey the rule.
    let window = solver.new_constraint_tag();
    if n >= 3 && m >= 3 {
        for i in 0..n - 2 {
            for j in 0..m - 2 {
                let lits: Vec<Lit> = (i..i + 3)
                    .flat_map(|a| (j..j + 3).map(move |b| (a, b)))
                    .map(|(a, b)| grid[a][b])
                    .collect();
                solver
                    .add_constraint(pumpkin_solver::boolean_less_than_or_equals(vec![1; 9], lits, 6, window))
                    .post();
            }
        }
    }

    // The dead cells just outside the region must not come alive: the live
    // cells next to each of them (up to three along an edge) are not exactly 3.
    let border = solver.new_constraint_tag();
    let mut outside: Vec<Vec<Lit>> = Vec::new();
    for j in 0..m {
        let cols = j.saturating_sub(1)..(j + 2).min(m);
        outside.push(cols.clone().map(|jj| grid[0][jj]).collect());
        outside.push(cols.map(|jj| grid[n - 1][jj]).collect());
    }
    for i in 0..n {
        let rows = i.saturating_sub(1)..(i + 2).min(n);
        outside.push(rows.clone().map(|ii| grid[ii][0]).collect());
        outside.push(rows.map(|ii| grid[ii][m - 1]).collect());
    }
    for lits in outside {
        let terms: Vec<Term> = lits.iter().map(|l| l.get_integer_variable().scaled(1)).collect();
        solver.add_constraint(pumpkin_solver::not_equals(terms, 3, border)).post();
    }

    // The objective is the number of live cells.
    let cells = n * m;
    let live = solver.new_bounded_integer(0, cells as i32);
    let all: Vec<Lit> = grid.iter().flatten().copied().collect();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(vec![1; cells], all, live, tag))
        .post();

    let mut out = Model::new();
    out.put("grid", grid);
    out.maximise(live);
    out
}
