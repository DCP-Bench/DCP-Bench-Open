// Solitaire battleships: fill a grid with water, submarines and the parts of
// longer ships (left, right, top, bottom, middle) so that the row and column
// counts hold, ships do not touch each other (not even diagonally), the fleet
// has the required number of ships of each size, and the given hints hold.

type Tag = pumpkin_solver::core::proof::ConstraintTag;

// Post "at least one of these literals is true".
fn post_clause(solver: &mut Solver, lits: Vec<Lit>, tag: Tag) {
    solver.add_constraint(pumpkin_solver::clause(lits, tag)).post();
}

// Post "exactly `count` of these literals are true".
fn post_count(solver: &mut Solver, lits: Vec<Lit>, count: i32, tag: Tag) {
    if lits.is_empty() {
        // An empty sum is 0, and Pumpkin cannot post an empty linear constraint.
        if count != 0 {
            let never = solver.get_false_literal();
            post_clause(solver, vec![never], tag);
        }
        return;
    }
    let total = solver.new_bounded_integer(count, count);
    let ones = vec![1; lits.len()];
    solver
        .add_constraint(pumpkin_solver::boolean_equals(ones, lits, total, tag))
        .post();
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let rows = inst.size("rows");
    let cols = inst.size("cols");
    let rowsum = inst.ints("rowsum"); // number of ship cells in each row
    let colsum = inst.ints("colsum"); // number of ship cells in each column
    let fleet = inst.matrix("fleet_counts"); // [ship size, how many of that size]
    let hints = inst.matrix("hints"); // [row, col, cell code], rows and cols counted from 0

    // The numbers a grid cell can hold. The instance names them; each is one of 0..7.
    let water = inst.size("WATER");
    let circle = inst.size("CIRCLE"); // a submarine, a ship of size 1
    let left = inst.size("LEFT");
    let right = inst.size("RIGHT");
    let top = inst.size("TOP");
    let bottom = inst.size("BOTTOM");
    let middle = inst.size("MIDDLE");

    // grid[r][c] is the code of cell (r, c), in 0..7 as in the reference.
    let grid: Vec<Vec<Var>> = (0..rows)
        .map(|_| (0..cols).map(|_| solver.new_bounded_integer(0, 7)).collect())
        .collect();

    // is[r][c][v] is true when cell (r, c) holds code v. Exactly one is true, and
    // grid[r][c] is the code. The constraints below are stated on these
    // Booleans because most of them are "this cell is X, so its neighbour is Y".
    let one_code = solver.new_constraint_tag();
    let channel = solver.new_constraint_tag();
    let is: Vec<Vec<Vec<Lit>>> = (0..rows)
        .map(|r| {
            (0..cols)
                .map(|c| {
                    let codes: Vec<Lit> = (0..8).map(|_| solver.new_literal()).collect();
                    post_clause(solver, codes.clone(), one_code);
                    solver
                        .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                            vec![1; 8], codes.clone(), 1, one_code))
                        .post();
                    // grid[r][c] == sum(v * is[v])
                    let mut terms: Vec<Term> = vec![grid[r][c].scaled(1)];
                    for v in 1..8 {
                        terms.push(codes[v].get_integer_variable().scaled(-(v as i32)));
                    }
                    solver
                        .add_constraint(pumpkin_solver::equals(terms, 0, channel))
                        .post();
                    codes
                })
                .collect()
        })
        .collect();
    let (rows_i, cols_i) = (rows as i32, cols as i32);
    let inside = |r: i32, c: i32| r >= 0 && r < rows_i && c >= 0 && c < cols_i;
    let at = |r: i32, c: i32, code: usize| -> Lit { is[r as usize][c as usize][code] };

    // The hints: the given cells hold the given codes.
    let hint_tag = solver.new_constraint_tag();
    for h in &hints {
        post_clause(solver, vec![at(h[0], h[1], h[2] as usize)], hint_tag);
    }

    // Row and column sums: the number of cells that are not water in each row
    // and column, i.e. cols - rowsum water cells in a row, rows - colsum in a column.
    let sums = solver.new_constraint_tag();
    for r in 0..rows_i {
        let waters: Vec<Lit> = (0..cols_i).map(|c| at(r, c, water)).collect();
        post_count(solver, waters, cols_i - rowsum[r as usize], sums);
    }
    for c in 0..cols_i {
        let waters: Vec<Lit> = (0..rows_i).map(|r| at(r, c, water)).collect();
        post_count(solver, waters, rows_i - colsum[c as usize], sums);
    }

    let touching = solver.new_constraint_tag();
    let shape = solver.new_constraint_tag();
    for r in 0..rows_i {
        for c in 0..cols_i {
            // No ships touch diagonally: of two diagonal neighbours at least
            // one is water. (Each unordered pair is listed once, from its upper cell.)
            for dc in [-1, 1] {
                if inside(r + 1, c + dc) {
                    post_clause(solver, vec![at(r, c, water), at(r + 1, c + dc, water)], touching);
                }
            }

            // A submarine is surrounded by water on all four sides.
            for (dr, dc) in [(-1, 0), (1, 0), (0, -1), (0, 1)] {
                if inside(r + dr, c + dc) {
                    post_clause(solver, vec![!at(r, c, circle), at(r + dr, c + dc, water)], shape);
                }
            }

            // An end piece of a ship has, on the side facing the rest of the
            // ship, a middle piece or the ship's other end, and water on its
            // other three sides. A left end faces right, a right end faces left,
            // a top end faces down and a bottom end faces up.
            for (piece, other_end, (dr, dc)) in [
                (left, right, (0, 1)),
                (right, left, (0, -1)),
                (top, bottom, (1, 0)),
                (bottom, top, (-1, 0)),
            ] {
                if inside(r + dr, c + dc) {
                    post_clause(
                        solver,
                        vec![!at(r, c, piece), at(r + dr, c + dc, middle), at(r + dr, c + dc, other_end)],
                        shape,
                    );
                } else {
                    // no room for the rest of the ship
                    post_clause(solver, vec![!at(r, c, piece)], shape);
                }
                for (er, ec) in [(-1, 0), (1, 0), (0, -1), (0, 1)] {
                    if (er, ec) != (dr, dc) && inside(r + er, c + ec) {
                        post_clause(solver, vec![!at(r, c, piece), at(r + er, c + ec, water)], shape);
                    }
                }
            }

            // A middle piece lies inside a horizontal ship (a left end or middle
            // to its left, a middle or right end to its right, water above and
            // below) or inside a vertical one (the same turned round).
            let mut ways: Vec<Lit> = vec![!at(r, c, middle)];
            if c > 0 && c < cols_i - 1 {
                let horizontal = solver.new_literal();
                post_clause(solver, vec![!horizontal, at(r, c - 1, left), at(r, c - 1, middle)], shape);
                post_clause(solver, vec![!horizontal, at(r, c + 1, right), at(r, c + 1, middle)], shape);
                for dr in [-1, 1] {
                    if inside(r + dr, c) {
                        post_clause(solver, vec![!horizontal, at(r + dr, c, water)], shape);
                    }
                }
                ways.push(horizontal);
            }
            if r > 0 && r < rows_i - 1 {
                let vertical = solver.new_literal();
                post_clause(solver, vec![!vertical, at(r - 1, c, top), at(r - 1, c, middle)], shape);
                post_clause(solver, vec![!vertical, at(r + 1, c, bottom), at(r + 1, c, middle)], shape);
                for dc in [-1, 1] {
                    if inside(r, c + dc) {
                        post_clause(solver, vec![!vertical, at(r, c + dc, water)], shape);
                    }
                }
                ways.push(vertical);
            }
            post_clause(solver, ways, shape);
        }
    }

    // Fleet: the number of submarines is the count listed for size 1.
    let fleet_tag = solver.new_constraint_tag();
    let submarines = fleet
        .iter()
        .find(|entry| entry[0] == 1)
        .expect("fleet_counts has no entry for size 1")[1];
    let all_circles: Vec<Lit> = (0..rows_i)
        .flat_map(|r| (0..cols_i).map(move |c| (r, c)))
        .map(|(r, c)| at(r, c, circle))
        .collect();
    post_count(solver, all_circles, submarines, fleet_tag);

    // Longer ships: a ship of `size` cells is a left end, size - 2 middle pieces
    // and a right end in a row, or a top, middle pieces and a bottom in a
    // column. placed[p] is true exactly when that pattern is on the grid at
    // placement p (both directions of the equivalence, since the placements are
    // counted), and the number of placements equals the count for that size.
    let placement = solver.new_constraint_tag();
    for entry in &fleet {
        let (size, count) = (entry[0], entry[1]);
        if size < 2 {
            continue;
        }
        let mut patterns: Vec<Vec<Lit>> = Vec::new();
        for r in 0..rows_i {
            for c in 0..=(cols_i - size) {
                let mut pieces = vec![at(r, c, left)];
                pieces.extend((1..size - 1).map(|k| at(r, c + k, middle)));
                pieces.push(at(r, c + size - 1, right));
                patterns.push(pieces);
            }
        }
        for r in 0..=(rows_i - size) {
            for c in 0..cols_i {
                let mut pieces = vec![at(r, c, top)];
                pieces.extend((1..size - 1).map(|k| at(r + k, c, middle)));
                pieces.push(at(r + size - 1, c, bottom));
                patterns.push(pieces);
            }
        }
        let mut placed: Vec<Lit> = Vec::new();
        for pieces in patterns {
            let p = solver.new_literal();
            for &piece in &pieces {
                post_clause(solver, vec![!p, piece], placement);
            }
            let mut all_present: Vec<Lit> = pieces.iter().map(|&piece| !piece).collect();
            all_present.push(p);
            post_clause(solver, all_present, placement);
            placed.push(p);
        }
        post_count(solver, placed, count, fleet_tag);
    }

    // No ship of a size the fleet does not list: every left end and every top
    // end starts one of the counted ships, so together they number the ships
    // longer than 1 in the fleet.
    let mut starts: Vec<Lit> = Vec::new();
    for r in 0..rows_i {
        for c in 0..cols_i {
            starts.push(at(r, c, left));
            starts.push(at(r, c, top));
        }
    }
    let longer: i32 = fleet.iter().filter(|entry| entry[0] > 1).map(|entry| entry[1]).sum();
    post_count(solver, starts, longer, fleet_tag);

    let mut m = Model::new();
    m.put("grid", grid);
    m
}
