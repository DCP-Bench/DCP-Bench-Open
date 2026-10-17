# csplib_011: ACC 1997/98 basketball double round-robin timetable.
# 9 teams (Clem, Duke, FSU, GT, UMD, UNC, NCSt, UVA, Wake), 18 dates (1-based in the
# statement, 0-based in the outputs). Satisfaction problem.
#
# Each team's venue sequence (H, A or B for bye) is chosen from a table of allowed
# sequences over the nine base dates (one per mirror pair). The mirror partner date
# carries the flipped venue of the same opponent, so the sequence over 18 dates follows.
# Host variables tie the sequences to the matches.
import itertools

import mip

# Mirroring scheme of Nemhauser and Trick (1-based dates).
PAIRS = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]
FLIP = {"H": "A", "A": "H", "B": "B"}

CLEM, DUKE, FSU, GT, UMD, UNC, NCSTATE, UVA, WAKE = range(9)
RIVAL = {DUKE: UNC, UNC: DUKE, CLEM: GT, GT: CLEM, NCSTATE: WAKE, WAKE: NCSTATE, UMD: UVA, UVA: UMD}


def expand(base_symbols, nd):
    """Venue string over dates 1..nd (index d-1) from one symbol per base date."""
    seq = [None] * nd
    for k, (r1, r2) in enumerate(PAIRS):
        seq[r1 - 1] = base_symbols[k]
        seq[r2 - 1] = FLIP[base_symbols[k]]
    return seq


def max_run(seq, chars):
    best = cur = 0
    for c in seq:
        cur = cur + 1 if c in chars else 0
        best = max(best, cur)
    return best


def pattern_ok(seq):
    # No team plays away on both last dates.
    if seq[16] == "A" and seq[17] == "A":
        return False
    # More than two away matches in a row; more than two home matches in a row.
    if max_run(seq, "A") > 2 or max_run(seq, "H") > 2:
        return False
    # More than three away matches or byes in a row; more than four home matches or byes in a row.
    if max_run(seq, "AB") > 3 or max_run(seq, "HB") > 4:
        return False
    # Weekends (even dates): four home, four away, one bye.
    weekends = [seq[d - 1] for d in range(2, 19, 2)]
    if weekends.count("H") != 4 or weekends.count("A") != 4 or weekends.count("B") != 1:
        return False
    # First five weekends: home matches or byes on at least two of them.
    if sum(1 for d in (2, 4, 6, 8, 10) if seq[d - 1] in "HB") < 2:
        return False
    return True


def team_pattern_ok(team, seq):
    # Other constraints of the statement that fix a team's venue or bye on a date.
    g = lambda d: seq[d - 1]
    if team == UNC and g(1) == "B":  # UNC does not have a bye in the first date
        return False
    if team in (CLEM, GT, WAKE, FSU) and g(1) == "A":  # Clem, FSU, GT, Wake not away in the first date
        return False
    if team in (CLEM, DUKE, UMD, WAKE) and g(18) == "A":  # Clem, Duke, UMD, Wake not away in the last date
        return False
    if team == WAKE and g(1) != "B":  # Wake has a bye in the first date
        return False
    if team == WAKE and g(17) == "H":  # Wake does not play home in date 17
        return False
    if team == DUKE and g(16) != "B":  # Duke has a bye in date 16
        return False
    if team in (FSU, NCSTATE) and g(18) == "B":  # Neither FSU nor NCSt has a bye in the last date
        return False
    return True


def build(instance):
    n = instance["n_teams"]
    nd = instance["n_days"]
    m = mip.Model(name="acc_basketball", solver_name="CBC")

    # Team patterns: one allowed venue sequence per team, chosen by a one-hot.
    patterns = {t: [] for t in range(n)}
    for symbols in itertools.product("HAB", repeat=len(PAIRS)):
        seq = expand(symbols, nd)
        if not pattern_ok(seq):
            continue
        for t in range(n):
            if team_pattern_ok(t, seq):
                patterns[t].append(seq)

    fol = {}
    for t in range(n):
        for k in range(len(patterns[t])):
            fol[t, k] = m.add_var(f"f_{t}_{k}", var_type=mip.BINARY)
        # Each team follows exactly one allowed sequence.
        m += mip.xsum(fol[t, k] for k in range(len(patterns[t]))) == 1

    # Two teams never share a sequence: equal base symbols on a mirror pair would mean
    # the two teams cannot meet on that pair, and every meeting lies on some pair.
    by_seq = {}
    for t in range(n):
        for k, seq in enumerate(patterns[t]):
            by_seq.setdefault(tuple(seq), []).append(fol[t, k])
    for terms in by_seq.values():
        if len(terms) > 1:
            m += mip.xsum(terms) <= 1

    def role(t, d, symbol):
        """Expression: team t has venue `symbol` on date d (1-based)."""
        return mip.xsum(
            fol[t, k] for k, seq in enumerate(patterns[t]) if seq[d - 1] == symbol
        )

    base_dates = [r1 for r1, _ in PAIRS]
    mirror_of = {}
    for r1, r2 in PAIRS:
        mirror_of[r1] = r2
        mirror_of[r2] = r1

    # host[b, i, j] (base date b): team i hosts team j. Only pairs compatible with the sequences.
    host = {}
    for b in base_dates:
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                can_home = any(seq[b - 1] == "H" for seq in patterns[i])
                can_away = any(seq[b - 1] == "A" for seq in patterns[j])
                if can_home and can_away:
                    host[b, i, j] = m.add_var(f"h_{b}_{i}_{j}", var_type=mip.BINARY)

    def host18(d, i, j):
        """Binary (or None) for team i hosting team j on date d (1..nd). Mirror dates swap roles."""
        if d in mirror_of and d not in base_dates:
            return host.get((mirror_of[d], j, i))
        return host.get((d, i, j))

    def meet(d, i, j):
        """List of variables that are 1 when i and j play each other on date d."""
        return [v for v in (host18(d, i, j), host18(d, j, i)) if v is not None]

    def away(d, i, j):
        """Variable (or None) for team i playing away at team j on date d."""
        return host18(d, j, i)

    # Mirroring. Each team plays the same team on the two dates of a mirror pair, with the
    # venues swapped (the mirror date's host variables are the base date's, transposed).
    # The host variables of each base date agree with the sequences.
    for b in base_dates:
        for i in range(n):
            home_i = mip.xsum(host[b, i, j] for j in range(n) if (b, i, j) in host)
            away_i = mip.xsum(host[b, j, i] for j in range(n) if (b, j, i) in host)
            m += home_i == role(i, b, "H")
            m += away_i == role(i, b, "A")
            for j in range(n):
                if (b, i, j) in host:
                    # Strengthening: i hosts j only if i is home and j is away on that date.
                    m += host[b, i, j] <= role(i, b, "H")
                    m += host[b, i, j] <= role(j, b, "A")

    # Double round robin with mirroring: each team pair meets exactly once, one home and one
    # away, on a mirror pair of dates. Each base date has four matches (one team has the bye).
    for i in range(n):
        for j in range(i + 1, n):
            m += mip.xsum(host[b, i, j] for b in base_dates if (b, i, j) in host) + mip.xsum(
                host[b, j, i] for b in base_dates if (b, j, i) in host
            ) == 1
    for b in base_dates:
        m += mip.xsum(host[b, i, j] for i in range(n) for j in range(n) if (b, i, j) in host) == n // 2

    # Rival matches. In the last date, every team except FSU plays its rival, unless it plays
    # FSU or has a bye.
    for t in range(n):
        if t == FSU:
            continue
        for x in range(n):
            if x in (t, RIVAL[t], FSU):
                continue
            for v in meet(nd, t, x):
                m += v == 0

    # Constrained matches. The following pairings must occur at least once in dates 11 to 18:
    # Wake-UNC, Wake-Duke, GT-UNC and GT-Duke.
    for i, j in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        terms = [v for d in range(11, nd + 1) for v in meet(d, i, j)]
        m += mip.xsum(terms) >= 1

    # Opponent sequence constraints. No team plays in two consecutive dates away against UNC
    # and Duke.
    for t in range(n):
        if t in (UNC, DUKE):
            continue
        for d in range(1, nd):
            for x, y in [(UNC, DUKE), (DUKE, UNC)]:
                terms = [v for v in (away(d, t, x), away(d + 1, t, y)) if v is not None]
                if len(terms) == 2:
                    m += mip.xsum(terms) <= 1
    # No team plays in three consecutive dates against UNC, Duke and Wake (independent of
    # home/away).
    for t in range(n):
        if t in (UNC, DUKE, WAKE):
            continue
        for d in range(1, nd - 1):
            terms = [v for k in (d, d + 1, d + 2) for x in (UNC, DUKE, WAKE) for v in meet(k, t, x)]
            m += mip.xsum(terms) <= 2

    # Other constraints: UNC plays Duke in the last date and in date 11; UNC plays Clem in
    # the second date.
    for d, i, j in [(nd, UNC, DUKE), (11, UNC, DUKE), (2, UNC, CLEM)]:
        m += mip.xsum(meet(d, i, j)) == 1

    # Output: config[d][i] is the opponent of team i on day d (0-based), and i itself on a bye.
    # where[d][i] is 0 for home, 1 for bye and 2 for away.
    config = []
    where = []
    for d in range(1, nd + 1):
        row_c = []
        row_w = []
        for i in range(n):
            row_c.append(i + mip.xsum((x - i) * v for x in range(n) if x != i for v in [host18(d, i, x)] if v is not None)
                         + mip.xsum((x - i) * v for x in range(n) if x != i for v in [host18(d, x, i)] if v is not None))
            home = mip.xsum(v for x in range(n) if x != i for v in [host18(d, i, x)] if v is not None)
            away_i = mip.xsum(v for x in range(n) if x != i for v in [host18(d, x, i)] if v is not None)
            row_w.append(1 - home + away_i)
        config.append(row_c)
        where.append(row_w)

    return m, {"config": config, "where": where}
