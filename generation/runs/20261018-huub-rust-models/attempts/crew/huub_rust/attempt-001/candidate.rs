// Crew assignment (crew). Assign the attendants to the flights (the instance gives
// the counts; a flight number is its index, a person number its index).
// Attribute columns: 0 steward, 1 hostess, 2 French, 3 Spanish, 4 German.
// Requirement columns: 0 crew size, 1 stewards, 2 hostesses, 3 French, 4 Spanish, 5 German.
// Output crew[f][p] is 1 when person p is assigned to flight f.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let attributes = inst.matrix("attributes");
    let required = inst.matrix("required_crew");
    let people = attributes.len();
    let flights = required.len();

    let mut crew: Vec<Vec<View<bool>>> = Vec::new();
    for _ in 0..flights {
        let row: Vec<View<bool>> = (0..people).map(|_| m.new_bool_decision()).collect();
        crew.push(row);
    }

    // Each flight needs a certain number of cabin crew.
    for f in 0..flights {
        let team: Vec<View<bool>> = crew[f].clone();
        m.linear(team.iter().copied().sum::<IntLinearExp>())
            .eq(required[f][0])
            .post()?;
    }

    // They have to speak certain languages, and each flight needs a certain number of stewards and hostesses.
    for f in 0..flights {
        for (col, req_col) in [(0usize, 1usize), (1, 2), (2, 3), (3, 4), (4, 5)] {
            let members: Vec<View<bool>> = (0..people)
                .filter(|&p| attributes[p][col] == 1)
                .map(|p| crew[f][p])
                .collect();
            m.linear(members.iter().copied().sum::<IntLinearExp>())
                .ge(required[f][req_col])
                .post()?;
        }
    }

    // Every cabin crew member has two flights off after an attended flight.
    for p in 0..people {
        for f in 0..flights {
            for k in 1..=2 {
                if f + k < flights {
                    let pair: Vec<View<bool>> = vec![crew[f][p], crew[f + k][p]];
                    m.linear(pair.iter().copied().sum::<IntLinearExp>())
                        .le(1)
                        .post()?;
                }
            }
        }
    }

    let mut out = Out::new();
    out.put("crew", crew);
    Ok(out)
}
