// KenKen: fill an n x n grid with the digits 1..n so that every row and column
// holds each digit once, and the digits in each cage reach the cage's result.
// The operation of a cage is not given: a cage of two cells may use +, -, x or /,
// a larger cage either + or x.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    // problem[p] = [result, [[row, col], ...]] (1-based). Cages differ in size,
    // so the field is ragged and is read from the raw JSON value.
    let cages: Vec<(i64, Vec<(usize, usize)>)> = inst
        .get("problem")
        .as_array()
        .expect("problem: expected an array of cages")
        .iter()
        .map(|cage| {
            let items = cage.as_array().expect("problem cage: expected [result, cells]");
            let result = items[0].as_i64().expect("problem cage: result must be an integer");
            let cells = items[1]
                .as_array()
                .expect("problem cage: expected a list of cells")
                .iter()
                .map(|cell| {
                    let rc = cell.as_array().expect("problem cell: expected [row, col]");
                    (
                        rc[0].as_i64().unwrap() as usize - 1,
                        rc[1].as_i64().unwrap() as usize - 1,
                    )
                })
                .collect();
            (result, cells)
        })
        .collect();

    let x: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(1, n as i32)).collect())
        .collect();

    // Each row contains each digit exactly once.
    let rows = solver.new_constraint_tag();
    for i in 0..n {
        solver.add_constraint(pumpkin_solver::all_different(x[i].clone(), rows)).post();
    }
    // Each column contains each digit exactly once.
    let cols = solver.new_constraint_tag();
    for j in 0..n {
        let column: Vec<Var> = (0..n).map(|i| x[i][j]).collect();
        solver.add_constraint(pumpkin_solver::all_different(column, cols)).post();
    }

    // Each cage reaches its result. The digit combinations that do so are listed
    // from the cage's result and size and posted as a table, which states the
    // "one of several operations" disjunction exactly:
    //   two cells a, b: a + b, a * b, a - b or b - a equals the result, or one
    //   divides into the other giving the result (a * result == b or b * result == a);
    //   any other size: the sum or the product of the digits equals the result.
    let cage_tag = solver.new_constraint_tag();
    let digits = n as i64;
    for (result, cells) in &cages {
        let k = cells.len();
        let res = *result;
        let mut rows_ok: Vec<Vec<i32>> = Vec::new();
        let mut tuple: Vec<i64> = vec![1; k];
        loop {
            let ok = if k == 2 {
                let (a, b) = (tuple[0], tuple[1]);
                a + b == res || a * b == res || a * res == b || b * res == a
                    || a - b == res || b - a == res
            } else {
                tuple.iter().sum::<i64>() == res || tuple.iter().product::<i64>() == res
            };
            if ok {
                rows_ok.push(tuple.iter().map(|&v| v as i32).collect());
            }
            // Advance to the next tuple of digits, odometer style.
            let mut pos = 0;
            while pos < k && tuple[pos] == digits {
                tuple[pos] = 1;
                pos += 1;
            }
            if pos == k {
                break;
            }
            tuple[pos] += 1;
        }
        let vars: Vec<Var> = cells.iter().map(|&(i, j)| x[i][j]).collect();
        solver
            .add_constraint(pumpkin_solver::table(vars, rows_ok, cage_tag))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
