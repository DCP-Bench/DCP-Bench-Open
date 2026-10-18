// Graph colouring of six countries (Belgium, Denmark, France, Germany,
// Netherlands, Luxembourg): assign each country a colour from 1 upwards so
// that neighbouring countries differ, minimising the number of colours used.
// Neighbour pairs come from the instance's graph field (1-based country numbers).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    const N: usize = 6;
    let edges = inst.matrix("graph");

    let colors = m.new_int_decisions(N, 1..=N as i64);

    // Two neighbouring countries cannot have the same colour.
    for e in &edges {
        let a = (e[0] - 1) as usize;
        let b = (e[1] - 1) as usize;
        m.linear(colors[a] - colors[b]).ne(0).post()?;
    }

    // The objective is the number of colours used, which is the largest colour.
    let ncol = m.new_int_decision(1..=N as i64);
    m.maximum(colors.clone()).result(ncol).post()?;

    let mut out = Out::new();
    out.put("colors", colors);
    out.minimise(ncol);
    Ok(out)
}
