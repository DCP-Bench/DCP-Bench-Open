// KenKen puzzle on an n x n grid, n read from the instance. The grid holds digits 1..n.
// Each cage is a group of cells with a target; the instance does not give the operation,
// so a cage is satisfied when one of the operations the description allows for its size gives the target.

// Enumerate the digit tuples for a cage of k cells that satisfy the cage target.
fn allowed_tuples(n: i64, k: usize, target: i64) -> Vec<Vec<i64>> {
    let mut rows = Vec::new();
    let mut tup = vec![1i64; k];
    loop {
        if cage_ok(&tup, target) {
            rows.push(tup.clone());
        }
        let mut i = 0;
        while i < k {
            if tup[i] < n {
                tup[i] += 1;
                break;
            }
            tup[i] = 1;
            i += 1;
        }
        if i == k {
            break;
        }
    }
    rows
}

fn cage_ok(v: &[i64], target: i64) -> bool {
    match v.len() {
        1 => v[0] == target,
        2 => {
            let (lo, hi) = (v[0].min(v[1]), v[0].max(v[1]));
            v[0] + v[1] == target
                || v[0] * v[1] == target
                || hi - lo == target
                || (lo > 0 && hi % lo == 0 && hi / lo == target)
        }
        _ => {
            let sum: i64 = v.iter().sum();
            let prod: i64 = v.iter().product();
            sum == target || prod == target
        }
    }
}

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    let nu = n as usize;

    // The grid: one digit variable per cell.
    let x: Vec<Vec<IntVar>> = (0..nu)
        .map(|_| (0..nu).map(|_| IntVar::new(1..=n)).collect())
        .collect();

    // Each row contains exactly one of each digit.
    for r in 0..nu {
        let row: Vec<IntVar> = x[r].clone();
        all_different(s, &row)?;
    }

    // Each column contains exactly one of each digit.
    for c in 0..nu {
        let col: Vec<IntVar> = (0..nu).map(|r| x[r][c].clone()).collect();
        all_different(s, &col)?;
    }

    // Each bold-outlined group of cells is a cage containing digits which
    // achieve the specified result using the specified mathematical operation.
    // (Digits may repeat within a group.)
    let cages = inst
        .get("problem")
        .as_array()
        .expect("problem is a list of cages");
    for cage in cages {
        let parts = cage.as_array().expect("cage is [target, cells]");
        let target = parts[0].as_i64().expect("cage target is an integer");
        let cells = parts[1].as_array().expect("cage cells are a list");
        let vars: Vec<IntVar> = cells
            .iter()
            .map(|p| {
                let rc = p.as_array().expect("cell is [row, col]");
                let r = rc[0].as_i64().expect("row") as usize - 1;
                let c = rc[1].as_i64().expect("col") as usize - 1;
                x[r][c].clone()
            })
            .collect();
        let rows = allowed_tuples(n, vars.len(), target);
        table(s, &vars, &rows)?;
    }

    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
