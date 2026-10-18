// Progressive party problem (CSPLib 013): timetable a party at a yacht club.
// Some boats are hosts and stay on board. The crews of the guest boats visit
// the host boats in several successive periods. Every boat holds at most its
// capacity, counting the host crew and all guest crews aboard. A guest boat
// cannot revisit a host, and guest crews cannot meet more than once.
// Minimise the number of host boats.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n_boats");
    let np = inst.size("n_periods");
    let cap = inst.ints("capacity");
    let crew = inst.ints("crew_size");
    let hi = n as i64 - 1;

    // Each boat is a host or a guest.
    let is_host: Vec<View<bool>> = (0..n).map(|_| m.new_bool_decision()).collect();

    // visits[p][b] is the boat that boat b is aboard in period p.
    let mut visits: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..np {
        visits.push(m.new_int_decisions(n, 0..=hi));
    }

    for p in 0..np {
        for b in 0..n {
            // A host boat stays where it is.
            m.linear(visits[p][b]).eq(b as i64).implied_by(is_host[b]).post()?;
            // Every boat visits a host boat in each period. A guest boat is
            // never its own host, so the visit is to some other host.
            for h in 0..n {
                let at_h = visits[p][b].eq(h as i64);
                m.linear([is_host[h]].into_iter().sum::<IntLinearExp>()).ge(1).implied_by(at_h).post()?;
            }
        }
    }

    // A guest boat cannot revisit a host: its visits in different periods differ.
    for b in 0..n {
        // guest is the negation of is_host[b].
        let guest = m.new_bool_decision();
        eq2(m, [is_host[b], guest].iter().copied().sum::<IntLinearExp>(), 1)?;
        for p in 0..np {
            for q in (p + 1)..np {
                m.linear(visits[p][b] - visits[q][b]).ne(0).implied_by(guest).post()?;
            }
        }
    }

    // Guest crews cannot meet more than once: two boats share a host in at most one period.
    for i in 0..n {
        for j in (i + 1)..n {
            let meets: Vec<View<bool>> = (0..np)
                .map(|p| m.linear(visits[p][i] - visits[p][j]).eq(0).reify())
                .collect();
            m.linear(meets.iter().copied().sum::<IntLinearExp>()).le(1).post()?;
        }
    }

    // Capacity: the crews aboard host h in each period, the host crew included, stay within its capacity.
    for p in 0..np {
        for h in 0..n {
            let load: IntLinearExp = (0..n)
                .map(|b| visits[p][b].eq(h as i64) * crew[b])
                .sum();
            m.linear(load).le(cap[h]).post()?;
        }
    }

    // Objective: the number of host boats.
    let hosts = m.new_int_decision(0..=(n as i64));
    m.linear(is_host.iter().copied().sum::<IntLinearExp>()).eq(hosts).post()?;

    let mut out = Out::new();
    out.put("is_host", is_host).put("visits", visits);
    out.minimise(hosts);
    Ok(out)
}
