# Initials queue: ten people in a queue, each with initials that are a pair of distinct
# letters from A..E in alphabetical order (letters are 0..4). All ten pairs are used once.
# No two neighbours in the queue share a letter. The front is BE, then CD, and the last
# person is BD. Output the queue of initials, front first, as 10 pairs of letters 0..4.
import mip

LETTERS = 5
PAIRS = [(a, b) for a in range(LETTERS) for b in range(a + 1, LETTERS)]  # 10 pairs
N = len(PAIRS)  # 10 people


def build(instance):
    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    m.verbose = 0
    m.max_mip_gap = 0.0
    m.max_mip_gap_abs = 0.0

    # x[p][s] = 1 when person p has the initials of pair s
    x = [[m.add_var(f"x_{p}_{s}", var_type=mip.BINARY) for s in range(N)] for p in range(N)]

    # each person has exactly one pair
    for p in range(N):
        m += mip.xsum(x[p][s] for s in range(N)) == 1

    # each pair is used by exactly one person
    for s in range(N):
        m += mip.xsum(x[p][s] for p in range(N)) == 1

    # the letters of the pair, per person: lett[p][L] = 1 when person p has letter L
    lett = [[mip.xsum(x[p][s] for s in range(N) if L in PAIRS[s]) for L in range(LETTERS)]
            for p in range(N)]

    # no-one shares a letter with the person in front of them
    # the people p and p+1 do not both have letter L
    for p in range(N - 1):
        for L in range(LETTERS):
            m += lett[p][L] + lett[p + 1][L] <= 1

    # the given front of the queue: BE, CD, and the last person BD
    pair_index = {pair: s for s, pair in enumerate(PAIRS)}
    m += x[0][pair_index[(1, 4)]] == 1
    m += x[1][pair_index[(2, 3)]] == 1
    m += x[N - 1][pair_index[(1, 3)]] == 1

    # the output: queue[p][k] is letter k of person p, an integer 0..4
    queue = [[m.add_var(f"queue_{p}_{k}", lb=0, ub=LETTERS - 1, var_type=mip.INTEGER)
              for k in range(2)] for p in range(N)]
    for p in range(N):
        m += queue[p][0] == mip.xsum(PAIRS[s][0] * x[p][s] for s in range(N))
        m += queue[p][1] == mip.xsum(PAIRS[s][1] * x[p][s] for s in range(N))

    # satisfaction problem: no objective
    return m, {"queue": queue}
