// Crossfigures (CSPLib 021): the numerical crossword. Fill a 9x9 grid with
// digits so that each across and down entry, read as a decimal number, meets its
// clue (a product, sum or quotient of other entries, a square, a prime, ...).
// Black squares hold 0.
//
// The instance has no fields: the grid, the entry positions and the clues are
// the puzzle's own data, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 9;
    let big = 9999; // every entry has at most four digits
    // The grid: '#' marks a black square.
    let layout = [
        "....#....",
        "..#...#..",
        ".#..#..#.",
        "....#....",
        "#.#####.#",
        "....#....",
        ".#..#..#.",
        "..#...#..",
        "....#....",
    ];

    let grid: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(0, 9)).collect())
        .collect();

    // Black squares hold 0.
    let blank = solver.new_constraint_tag();
    for r in 0..n {
        for c in 0..n {
            if layout[r].as_bytes()[c] == b'#' {
                solver.add_constraint(pumpkin_solver::equals(vec![grid[r][c]], 0, blank)).post();
            }
        }
    }

    // An entry is the number written by its digits: `len` cells starting at
    // (row, col), 1-based, going across or down.
    let digits = solver.new_constraint_tag();
    let entry = |solver: &mut Solver, len: usize, row: usize, col: usize, across: bool| -> Var {
        let value = solver.new_bounded_integer(0, big);
        let mut terms: Vec<Term> = vec![value.scaled(-1)];
        for i in 0..len {
            let (r, c) = if across { (row - 1, col - 1 + i) } else { (row - 1 + i, col - 1) };
            terms.push(grid[r][c].scaled(10i32.pow((len - 1 - i) as u32)));
        }
        solver.add_constraint(pumpkin_solver::equals(terms, 0, digits)).post();
        value
    };

    // Across entries: (length, row, column).
    let a1 = entry(solver, 4, 1, 1, true);
    let a4 = entry(solver, 4, 1, 6, true);
    let a7 = entry(solver, 2, 2, 1, true);
    let a8 = entry(solver, 3, 2, 4, true);
    let a9 = entry(solver, 2, 2, 8, true);
    let a10 = entry(solver, 2, 3, 3, true);
    let a11 = entry(solver, 2, 3, 6, true);
    let a13 = entry(solver, 4, 4, 1, true);
    let a15 = entry(solver, 4, 4, 6, true);
    let a17 = entry(solver, 4, 6, 1, true);
    let a20 = entry(solver, 4, 6, 6, true);
    let a23 = entry(solver, 2, 7, 3, true);
    let a24 = entry(solver, 2, 7, 6, true);
    let a25 = entry(solver, 2, 8, 1, true);
    let a27 = entry(solver, 3, 8, 4, true);
    let a28 = entry(solver, 2, 8, 8, true);
    let a29 = entry(solver, 4, 9, 1, true);
    let a30 = entry(solver, 4, 9, 6, true);
    // Down entries: (length, row, column).
    let d1 = entry(solver, 4, 1, 1, false);
    let d2 = entry(solver, 2, 1, 2, false);
    let d3 = entry(solver, 4, 1, 4, false);
    let d4 = entry(solver, 4, 1, 6, false);
    let d5 = entry(solver, 2, 1, 8, false);
    let d6 = entry(solver, 4, 1, 9, false);
    let d10 = entry(solver, 2, 3, 3, false);
    let d12 = entry(solver, 2, 3, 7, false);
    let d14 = entry(solver, 3, 4, 2, false);
    let d16 = entry(solver, 3, 4, 8, false);
    let d17 = entry(solver, 4, 6, 1, false);
    let d18 = entry(solver, 2, 6, 3, false);
    let d19 = entry(solver, 4, 6, 4, false);
    let d20 = entry(solver, 4, 6, 6, false);
    let d21 = entry(solver, 2, 6, 7, false);
    let d22 = entry(solver, 4, 6, 9, false);
    let d26 = entry(solver, 2, 8, 2, false);
    let d28 = entry(solver, 2, 8, 8, false);

    // Linear clues, each written as a*x + b*y + ... == rhs over the entries.
    let clues = solver.new_constraint_tag();
    let linear: Vec<(Vec<Term>, i32)> = vec![
        (vec![a1.scaled(1), a27.scaled(-2)], 0),   // A1: 27 across times two
        (vec![a4.scaled(1), d4.scaled(-1)], 71),   // A4: 4 down plus seventy-one
        (vec![a7.scaled(1), d18.scaled(-1)], 4),   // A7: 18 down plus four
        (vec![a8.scaled(16), d6.scaled(-1)], 0),   // A8: 6 down divided by sixteen
        (vec![a9.scaled(1), d2.scaled(-1)], -18),  // A9: 2 down minus eighteen
        (vec![a10.scaled(12)], 6 * 144),           // A10: dozens in six gross
        (vec![a11.scaled(1), d5.scaled(-1)], -70), // A11: 5 down minus seventy
        (vec![a15.scaled(1), d6.scaled(-1)], -350), // A15: 6 down minus 350
        (vec![a25.scaled(17), a20.scaled(-1)], 0), // A25: 20 across divided by seventeen
        (vec![a27.scaled(4), d6.scaled(-1)], 0),   // A27: 6 down divided by four
        (vec![a28.scaled(1)], 4 * 12),             // A28: four dozen
        (vec![a29.scaled(1)], 7 * 144),            // A29: seven gross
        (vec![a30.scaled(1), d22.scaled(-1)], 450), // A30: 22 down plus 450
        (vec![d1.scaled(1), a1.scaled(-1)], 27),   // D1: 1 across plus twenty-seven
        (vec![d2.scaled(1)], 5 * 12),              // D2: five dozen
        (vec![d3.scaled(1), a30.scaled(-1)], 888), // D3: 30 across plus 888
        (vec![d4.scaled(1), a17.scaled(-2)], 0),   // D4: two times 17 across
        (vec![d5.scaled(12), a29.scaled(-1)], 0),  // D5: 29 across divided by twelve
        (vec![d10.scaled(1), a10.scaled(-1)], 4),  // D10: 10 across plus four
        (vec![d12.scaled(1), a24.scaled(-3)], 0),  // D12: three times 24 across
        (vec![d14.scaled(16), a13.scaled(-1)], 0), // D14: 13 across divided by sixteen
        (vec![d16.scaled(1), d28.scaled(-15)], 0), // D16: 28 down times fifteen
        (vec![d17.scaled(1), a13.scaled(-1)], -399), // D17: 13 across minus 399
        (vec![d18.scaled(18), a29.scaled(-1)], 0), // D18: 29 across divided by eighteen
        (vec![d19.scaled(1), d22.scaled(-1)], -94), // D19: 22 down minus ninety-four
        (vec![d20.scaled(1), a20.scaled(-1)], -9), // D20: 20 across minus nine
        (vec![d21.scaled(1), a25.scaled(-1)], -52), // D21: 25 across minus fifty-two
        (vec![d22.scaled(1), d20.scaled(-6)], 0),  // D22: 20 down times six
        (vec![d26.scaled(1), a24.scaled(-5)], 0),  // D26: five times 24 across
        (vec![d28.scaled(1), d21.scaled(-1)], 27), // D28: 21 down plus twenty-seven
    ];
    for (terms, rhs) in linear {
        solver.add_constraint(pumpkin_solver::equals(terms, rhs, clues)).post();
    }

    // Product clues: A13 is 26 down times 23 across, A17 is 25 across times 23
    // across, D6 is 28 across times 23 across.
    for (x, y, product) in [(d26, a23, a13), (a25, a23, a17), (a28, a23, d6)] {
        solver.add_constraint(pumpkin_solver::times(x, y, product, clues)).post();
    }

    // A20 and A24 are square numbers, A23 is a prime: membership in the list of
    // squares or primes up to 9999, posted as a one-column table.
    let is_prime = |v: i32| v >= 2 && (2..).take_while(|d| d * d <= v).all(|d| v % d != 0);
    let squares: Vec<Vec<i32>> = (1..=100).map(|i| i * i).filter(|&s| s <= big).map(|s| vec![s]).collect();
    let primes: Vec<Vec<i32>> = (2..=big).filter(|&v| is_prime(v)).map(|v| vec![v]).collect();
    solver.add_constraint(pumpkin_solver::table(vec![a20], squares.clone(), clues)).post();
    solver.add_constraint(pumpkin_solver::table(vec![a24], squares, clues)).post();
    solver.add_constraint(pumpkin_solver::table(vec![a23], primes, clues)).post();

    let mut m = Model::new();
    m.put("M", grid);
    m
}
