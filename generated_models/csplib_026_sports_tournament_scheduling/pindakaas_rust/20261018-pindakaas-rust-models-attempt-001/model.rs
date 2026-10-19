// CSPLib 026: sports tournament scheduling.
// n teams (n even) play over n-1 weeks. Each week has n/2 periods, and each period has
// two slots: the first team plays at home, the second plays away.
// Outputs home[w][p] and away[w][p] as 1-based team numbers.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n_teams");
    let nn = n as i64;
    let weeks = n - 1;
    let periods = n / 2;

    let mut home: Vec<Vec<IntVar>> = Vec::new();
    let mut away: Vec<Vec<IntVar>> = Vec::new();
    for _ in 0..weeks {
        let mut hr = Vec::new();
        let mut ar = Vec::new();
        for _ in 0..periods {
            hr.push(IntVar::new(1..=nn));
            ar.push(IntVar::new(1..=nn));
        }
        home.push(hr);
        away.push(ar);
    }

    // every team plays once a week
    for w in 0..weeks {
        let mut week: Vec<IntVar> = Vec::new();
        week.extend(home[w].iter().cloned());
        week.extend(away[w].iter().cloned());
        all_different(s, &week)?;
    }

    // e[w][p][t]: team t plays in period p of week w, at home or away
    let mut e: Vec<Vec<Vec<Lit>>> = Vec::new();
    for w in 0..weeks {
        let mut ew: Vec<Vec<Lit>> = Vec::new();
        for p in 0..periods {
            let mut ep: Vec<Lit> = Vec::new();
            for t in 1..=nn {
                let bh = home[w][p].equals(s, t)?;
                let eh = lit_of(s, bh)?;
                let ba = away[w][p].equals(s, t)?;
                let ea = lit_of(s, ba)?;
                let l = s.new_lit();
                s.add_clause([!eh, l])?;
                s.add_clause([!ea, l])?;
                s.add_clause([!l, eh, ea])?;
                ep.push(l);
            }
            ew.push(ep);
        }
        e.push(ew);
    }

    // every team plays at most twice in the same period over the tournament
    for p in 0..periods {
        for t in 0..n {
            let mut sum = LinExp::default();
            for w in 0..weeks {
                sum += bx(BoolVal::Lit(e[w][p][t]));
            }
            post(s, sum, Comparator::LessEq, 2)?;
        }
    }

    // every team plays every other team
    // c <-> both teams are in the same period of the same week, which means they meet there
    for i in 0..n {
        for j in (i + 1)..n {
            let mut sum = LinExp::default();
            for w in 0..weeks {
                for p in 0..periods {
                    let c = s.new_lit();
                    let (a, b) = (e[w][p][i], e[w][p][j]);
                    s.add_clause([!c, a])?;
                    s.add_clause([!c, b])?;
                    s.add_clause([c, !a, !b])?;
                    sum += bx(BoolVal::Lit(c));
                }
            }
            post(s, sum, Comparator::Equal, 1)?;
        }
    }

    let mut out = Out::new();
    out.put("home", &home).put("away", &away);
    Ok(out)
}
