// Template design (csplib_002): decide how many templates to print, which
// variations go on each template and how many copies of each. The printed
// sheets must cover the demand of every variation. Minimise the number of
// printed sheets.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let nt = inst.size("n_templates");
    let nv = inst.size("n_var");
    let slots = inst.int("n_slots");
    let demand = inst.ints("demand");
    let total: i64 = demand.iter().sum();

    // Number of sheets printed from each template
    let mut production: Vec<View<i64>> = Vec::new();
    for _ in 0..nt {
        production.push(m.new_int_decision(0..=total));
    }

    // Copies of each variation on each template
    let mut layout: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..nt {
        let mut row: Vec<View<i64>> = Vec::new();
        for _ in 0..nv {
            row.push(m.new_int_decision(0..=slots));
        }
        layout.push(row);
    }

    // Each template holds at most n_slots variations
    for t in 0..nt {
        let used = layout[t].iter().copied().sum::<IntLinearExp>();
        m.linear(used).le(slots).post()?;
    }

    // Copies printed of each variation from a template: sheets times copies on it
    let mut printed: Vec<Vec<View<i64>>> = Vec::new();
    for t in 0..nt {
        let mut row: Vec<View<i64>> = Vec::new();
        for j in 0..nv {
            let q = m.mul(production[t], layout[t][j]).define();
            m.linear(q).le(total * slots).post()?;
            row.push(q);
        }
        printed.push(row);
    }

    // The printed copies must cover the demand of every variation
    for j in 0..nv {
        let col = (0..nt).map(|t| printed[t][j]).sum::<IntLinearExp>();
        m.linear(col).ge(demand[j]).post()?;
    }

    // Objective: the number of printed sheets, summed over the templates
    let sheets = m.new_int_decision(0..=total * (nt as i64));
    m.linear(production.iter().copied().sum::<IntLinearExp>())
        .eq(sheets)
        .post()?;

    let mut out = Out::new();
    out.put("layout", layout).put("production", production);
    out.minimise(sheets);
    Ok(out)
}
