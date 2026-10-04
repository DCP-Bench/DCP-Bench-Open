# The rehearsal problem (CSPLib 39): order the pieces of a concert rehearsal so
# that the total time players spend present but not playing is minimal. A
# player arrives just before their first piece and leaves just after their last.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    num_pieces = instance["num_pieces"]
    num_players = instance["num_players"]
    duration = instance["duration"]
    rehearsal = instance["rehearsal"]   # rehearsal[p][j] = 1 if player p plays in piece j
    slots = range(num_pieces)

    pool = IDPool()
    # rehearsal_order[i] is the piece rehearsed in slot i. Its direct-encoding
    # literal at[i][j] ("slot i holds piece j") is what the clauses use.
    order = [Integer(f"rehearsal_order{i}", 0, max(num_pieces - 1, 1), vpool=pool)
             for i in slots]
    at = [[order[i].equals(j) for j in range(num_pieces)] for i in slots]

    formula = WCNF()
    formula.extend(IntegerEngine(vars=order, vpool=pool).clausify().clauses)
    # The domain is widened to two values when there is a single piece, so
    # no Integer has one value; that extra value is ruled out here.
    if num_pieces == 1:
        formula.append([-order[0].equals(1)])

    # Each piece is rehearsed exactly once, so the order is a permutation.
    for j in range(num_pieces):
        formula.extend(CardEnc.equals(lits=[at[i][j] for i in slots], bound=1,
                                      vpool=pool, encoding=EncType.seqcounter).clauses)

    for p in range(num_players):
        mine = [j for j in range(num_pieces) if rehearsal[p][j] == 1]
        # plays[i]: player p plays in the piece at slot i.
        plays = [pool.id(("plays", p, i)) for i in slots]
        for i in slots:
            for j in mine:
                formula.append([-at[i][j], plays[i]])
        # arrived[i]: player p has played at slot i or earlier, so has arrived
        # by slot i. left[i]: player p plays at slot i or later, so has not
        # yet departed. Only the direction that forces presence is stated:
        # the objective never gains from making a player present, so an
        # optimal answer keeps these false wherever the plays allow.
        arrived = [pool.id(("arrived", p, i)) for i in slots]
        left = [pool.id(("still", p, i)) for i in slots]
        for i in slots:
            formula.append([-plays[i], arrived[i]])
            formula.append([-plays[i], left[i]])
            if i > 0:
                formula.append([-arrived[i - 1], arrived[i]])
            if i + 1 < num_pieces:
                formula.append([-left[i + 1], left[i]])

        # Minimise the total waiting time: player p is waiting during slot i
        # when present there (arrived and not yet departed) while the piece in
        # that slot is one they do not play; that costs the piece's duration.
        for i in slots:
            for j in range(num_pieces):
                if rehearsal[p][j] == 0 and duration[j] > 0:
                    formula.append([-arrived[i], -left[i], -at[i][j]], weight=duration[j])

    return formula, {"rehearsal_order": order}
