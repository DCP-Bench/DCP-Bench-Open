// A Latin square of order m with the QG3 property (a*b)*(b*a) = a.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let order = inst.size("m");
    let top = order as i32 - 1;

    let q = cp.grid(order, order, 0, top);
    for i in 0..order {
        cp.all_different(terms(&q[i]));
        let column: Vec<Var> = (0..order).map(|r| q[r][i]).collect();
        cp.all_different(terms(&column));
    }

    // q[q[a][b]][q[b][a]] == a, over the row-major flattening of q, because
    // element indexes one array with one index.
    let flat: Vec<Var> = q.iter().flatten().copied().collect();
    let cells = terms(&flat);
    for a in 0..order {
        for b in 0..order {
            let index = cp.int(0, (order * order) as i32 - 1);
            cp.eq(vec![c(order as i32, q[a][b]), t(q[b][a]), c(-1, index)], 0);
            let target = cp.constant(a as i32);
            cp.element(index, cells.clone(), target);
        }
    }

    let mut m = Model::new();
    m.put("quasigroup", q);
    m
}
