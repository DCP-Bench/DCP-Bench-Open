// Huey, Dewey and Louie are being questioned by their uncle. Each statement is
// made by a cub scout who cannot tell a lie, so every statement is true.
// Output: huey, dewey, louie are guilty (true) or not guilty (false).

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let huey = m.new_bool_decision();
    let dewey = m.new_bool_decision();
    let louie = m.new_bool_decision();

    // Huey: Dewey and Louie has equal share in it; if one is guilty, so is the other.
    m.proposition(!BoolFormula::Atom(dewey) | BoolFormula::Atom(louie)).post()?;
    m.proposition(BoolFormula::Atom(dewey) | !BoolFormula::Atom(louie)).post()?;

    // Dewey: If Huey is guilty, then so am I.
    m.proposition(!BoolFormula::Atom(huey) | BoolFormula::Atom(dewey)).post()?;

    // Louie: Dewey and I are not both guilty.
    m.proposition(!BoolFormula::Atom(dewey) | !BoolFormula::Atom(louie)).post()?;

    let mut out = Out::new();
    out.put("dewey", dewey).put("huey", huey).put("louie", louie);
    Ok(out)
}
