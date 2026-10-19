// Template design (csplib_002): decide the number of templates, which variations and how many
// copies of each go on each template, and how many sheets each template is printed. Minimise
// the total number of printed sheets.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let nt = inst.size("n_templates");
    let nv = inst.size("n_var");
    let slots = inst.int("n_slots");
    let demand = inst.ints("demand");
    let total: i64 = demand.iter().sum();
    let ub = demand.iter().copied().max().unwrap_or(0);

    // Each template is printed a number of times, at least once.
    // production[t] is the number of printed sheets of template t.
    let production: Vec<View<i64>> = (0..nt).map(|_| m.new_int_decision(1..=ub)).collect();

    // The variations are etched on a template: the number of copies of each variation on a
    // template is at most the number of slots, and the template is full.
    // layout[t][j] is the number of copies of variation j on template t.
    let layout: Vec<Vec<View<i64>>> = (0..nt)
        .map(|_| (0..nv).map(|_| m.new_int_decision(0..=slots)).collect())
        .collect();

    // Each mother sheet holds exactly n_slots variations, so every template is full.
    for t in 0..nt {
        m.linear(layout[t].iter().copied().sum::<IntLinearExp>()).eq(slots).post()?;
    }

    // The number of copies of variation j printed from template t is production[t] times
    // layout[t][j], since every printed sheet carries the same copies.
    let mut printed: Vec<Vec<View<i64>>> = Vec::new();
    for t in 0..nt {
        let mut row = Vec::new();
        for j in 0..nv {
            let q = m.new_int_decision(0..=ub * slots);
            m.mul(production[t], layout[t][j]).result(q).post()?;
            row.push(q);
        }
        printed.push(row);
    }

    // The order asks for a quantity of each variation: the copies printed of variation j, summed
    // over all templates, must cover its demand.
    for j in 0..nv {
        m.linear((0..nt).map(|t| printed[t][j]).sum::<IntLinearExp>()).ge(demand[j]).post()?;
    }

    // The number of printed sheets is the sum of the productions of all templates.
    let sheets = m.new_int_decision(nt as i64..=ub * nt as i64);
    m.linear(production.iter().copied().sum::<IntLinearExp>() - sheets).eq(0).post()?;

    // Every sheet carries n_slots variations, so the sheets printed must cover the total demand.
    m.linear(sheets * slots).ge(total).post()?;

    let mut out = Out::new();
    out.put("layout", layout).put("production", production);
    out.minimise(sheets);
    Ok(out)
}
