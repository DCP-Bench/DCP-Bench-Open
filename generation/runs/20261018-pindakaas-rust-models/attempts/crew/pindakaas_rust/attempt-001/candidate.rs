// Crew assignment (satisfaction problem): assign 20 flight attendants to 10 flights.
// Each flight needs a certain number of cabin crew, and they have to speak certain languages.
// Every cabin crew member has two flights off after an attended flight.
// Output crew[f][p] = 1 when person p is assigned to flight f.
//
// Instance layout: attributes[p] = [steward, hostess, French, Spanish, German];
// required_crew[f] = [total crew, stewards, hostesses, French, Spanish, German].

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let attributes = inst.matrix("attributes");
    let required = inst.matrix("required_crew");
    let np = attributes.len();
    let nf = required.len();

    let mut crew: Vec<Vec<Lit>> = Vec::new();
    for _ in 0..nf {
        let row: Vec<Lit> = (0..np).map(|_| s.new_lit()).collect();
        crew.push(row);
    }

    // Each flight needs a certain number of cabin crew.
    for f in 0..nf {
        let mut e = LinExp::default();
        for p in 0..np {
            e += LinExp::from(crew[f][p].clone());
        }
        post(s, e, Comparator::Equal, required[f][0])?;
    }

    // they have to speak certain languages: each flight needs at least the required number
    // of attendants with each attribute (stewards, hostesses, French, Spanish, German).
    for f in 0..nf {
        for j in 1..6 {
            let mut e = LinExp::default();
            for p in 0..np {
                if attributes[p][j - 1] == 1 {
                    e += LinExp::from(crew[f][p].clone());
                }
            }
            post(s, e, Comparator::GreaterEq, required[f][j])?;
        }
    }

    // Every cabin crew member has two flights off after an attended flight.
    for p in 0..np {
        for f in 0..nf {
            for d in 1..=2 {
                if f + d < nf {
                    s.add_clause([!crew[f][p].clone(), !crew[f + d][p].clone()])?;
                }
            }
        }
    }

    let mut out = Out::new();
    out.put("crew", &crew);
    Ok(out)
}
