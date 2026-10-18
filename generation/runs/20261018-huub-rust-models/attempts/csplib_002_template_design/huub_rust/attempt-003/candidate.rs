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
    let dmax: i64 = demand.iter().copied().max().unwrap_or(0);

    // Copies of each variation on each template, created first so that the
    // small layout domains are decided before the sheet counts.
    let mut layout: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..nt {
        let mut row: Vec<View<i64>> = Vec::new();
        for _ in 0..nv {
            row.push(m.new_int_decision(0..=slots));
        }
        layout.push(row);
    }

    // Number of sheets printed from each template. More sheets than the
    // largest demand is never needed, so this bound loses no optimum.
    let mut production: Vec<View<i64>> = Vec::new();
    for _ in 0..nt {
        production.push(m.new_int_decision(0..=dmax));
    }

    // Each template holds at most n_slots variations
    for t in 0..nt {
        let used = layout[t].iter().copied().sum::<IntLinearExp>();
        m.linear(used).le(slots).post()?;
    }

    // Copies printed of each variation from a template: sheets times copies on it.
    // Written out per possible copy count k: the Boolean choice[k] says the layout
    // value is k, and then the printed copies equal k times the sheets.
    let mut printed: Vec<Vec<View<i64>>> = Vec::new();
    for t in 0..nt {
        let mut row: Vec<View<i64>> = Vec::new();
        for j in 0..nv {
            let q = m.new_int_decision(0..=dmax * slots);
            let mut choice: Vec<View<bool>> = Vec::new();
            for k in 0..=slots {
                let b = m.new_bool_decision();
                m.linear(layout[t][j]).eq(k).implied_by(b).post()?;
                m.linear(q - production[t] * k).le(0).implied_by(b).post()?;
                m.linear(q - production[t] * k).ge(0).implied_by(b).post()?;
                choice.push(b);
            }
            m.linear(choice.iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
            row.push(q);
        }
        printed.push(row);
    }

    // The printed copies must cover the demand of every variation
    for j in 0..nv {
        let col = (0..nt).map(|t| printed[t][j]).sum::<IntLinearExp>();
        m.linear(col).ge(demand[j]).post()?;
    }

    // Each sheet from a template carries at most n_slots copies, so the copies
    // printed from a template are at most n_slots times its sheets
    for t in 0..nt {
        let copies = (0..nv).map(|j| printed[t][j]).sum::<IntLinearExp>();
        m.linear(copies - production[t] * slots).le(0).post()?;
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
