// SONET (CSPLib prob056): nodes are placed on rings through add-drop multiplexers (ADMs).
// Each node pair with a demand must share at least one ring. Each ring k hosts at most
// capacity_nodes[k] nodes. Minimise the total number of ADMs used.
// ring_config[k][i] is 1 if node i is on ring k. total_adms is the number of ADMs.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let r = inst.size("r");
    let demand = inst.matrix("demand");
    let cap = inst.ints("capacity_nodes");

    // ring_config: node i is installed on ring k.
    let mut x: Vec<Vec<View<bool>>> = Vec::new();
    for _ in 0..r {
        let mut row = Vec::new();
        for _ in 0..n {
            row.push(m.new_bool_decision());
        }
        x.push(row);
    }

    // Each ring hosts at most capacity_nodes[k] nodes.
    for k in 0..r {
        let load: IntLinearExp = x[k].iter().copied().sum();
        m.linear(load).le(cap[k]).post()?;
    }

    // For two nodes with a demand between them, they must be on at least one common ring.
    for i in 0..n {
        for j in (i + 1)..n {
            if demand[i][j] == 0 && demand[j][i] == 0 {
                continue;
            }
            let mut shared = Vec::new();
            for k in 0..r {
                // z implies that both nodes i and j are on ring k.
                let z = m.new_bool_decision();
                let both: IntLinearExp = [x[k][i], x[k][j]].into_iter().sum();
                m.linear(both).ge(2).implied_by(z).post()?;
                shared.push(z);
            }
            let any: IntLinearExp = shared.iter().copied().sum();
            m.linear(any).ge(1).post()?;
        }
    }

    // total_adms: the number of ADMs, that is the number of (node, ring) installations.
    let all: IntLinearExp = x.iter().flatten().copied().sum();
    let total = m.new_int_decision(0..=((r * n) as i64));
    m.linear(all).eq(total).post()?;

    let mut out = Out::new();
    out.put("ring_config", x).put("total_adms", total);
    out.minimise(total);
    Ok(out)
}
