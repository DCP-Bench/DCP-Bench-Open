# ACC basketball schedule: a double round-robin timetable for the 9 teams of the 1997/98
# Atlantic Coast Conference over 18 dates (every team plays every other team once at home and
# once away; odd dates are weekdays, even dates weekends), subject to the mirroring, final
# date, pattern, weekend, rival, constrained-match, opponent-sequence and special constraints.
using JuMP

function build(instance)
    n_teams = instance["n_teams"]
    n_days = instance["n_days"]

    # The teams, numbered from 1 here (the printed answer numbers them from 0), and the
    # tournament's own constants: these belong to the 1997/98 ACC problem, not to the instance.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = 1, 2, 3, 4, 5, 6, 7, 8, 9
    # the traditional rival of every team (FSU has none and is listed as its own rival)
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]
    # Nemhauser and Trick's mirroring scheme: dates (r1, r2) have the same opponents, with home
    # and away swapped
    mirror_pairs = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]
    weekends = 2:2:n_days   # the even dates are the weekend fixtures
    teams = 1:n_teams
    days = 1:n_days
    final_day = n_days

    mirror_of = zeros(Int, n_days)
    for (a, b) in mirror_pairs
        mirror_of[a] = b
        mirror_of[b] = a
    end

    model = Model()

    # host[d, t, u] = 1 when team t plays at home against team u on date d. A match is
    # described once, from the home side, so "a plays b" and "who is home" cannot disagree. By
    # the mirroring constraint, the second date of a pair is the first with home and away
    # swapped, so it reuses the first date's variables with the two teams exchanged.
    host = Dict{Tuple{Int,Int,Int},VariableRef}()
    for d in days, t in teams, u in teams
        t == u && continue
        if mirror_of[d] < d
            host[(d, t, u)] = host[(mirror_of[d], u, t)]
        else
            host[(d, t, u)] = @variable(model, binary = true)
        end
    end

    # plays[d, t, u] = 1 when t and u meet on date d (either at home); home[d, t] and away[d, t]
    # = 1 when team t plays at home or away on date d; bye[d, t] = 1 when it has no match.
    plays(d, t, u) = host[(d, t, u)] + host[(d, u, t)]
    home(d, t) = sum(host[(d, t, u)] for u in teams if u != t)
    away(d, t) = sum(host[(d, u, t)] for u in teams if u != t)
    bye(d, t) = 1 - home(d, t) - away(d, t)

    # a team plays at most one match a date (otherwise it has a bye)
    @constraint(model, [d = days, t = teams], home(d, t) + away(d, t) <= 1)

    # Double round-robin: each team plays each other team once at home and once away
    @constraint(model, [t = teams, u = teams; t != u], sum(host[(d, t, u)] for d in days) == 1)

    # 2. No team plays away on both of the last two dates
    @constraint(model, [t = teams], away(final_day - 1, t) + away(final_day, t) <= 1)

    # 3. Home/away/bye patterns
    for t in teams
        for d in 1:n_days-2
            # no more than two home matches in a row, and no more than two away matches in a row
            @constraint(model, sum(home(e, t) for e in d:d+2) <= 2)
            @constraint(model, sum(away(e, t) for e in d:d+2) <= 2)
        end
        for d in 1:n_days-3
            # no more than three away matches or byes in a row
            @constraint(model, sum(away(e, t) + bye(e, t) for e in d:d+3) <= 3)
        end
        for d in 1:n_days-4
            # no more than four home matches or byes in a row
            @constraint(model, sum(home(e, t) + bye(e, t) for e in d:d+4) <= 4)
        end
    end

    # 4. Weekend pattern: on the weekends each team plays four at home, four away and has one bye
    @constraint(model, [t = teams], sum(home(d, t) for d in weekends) == 4)
    @constraint(model, [t = teams], sum(away(d, t) for d in weekends) == 4)
    @constraint(model, [t = teams], sum(bye(d, t) for d in weekends) == 1)

    # 5. First weekends: each team has home matches or byes on at least two of the first five weekends
    @constraint(model, [t = teams], sum(home(d, t) + bye(d, t) for d in weekends[1:5]) >= 2)

    # 6. Rival matches: on the last date every team except FSU plays its rival, unless it plays FSU
    #    or has a bye
    for t in teams
        t == FSU && continue
        @constraint(model, bye(final_day, t) + plays(final_day, t, rivals[t]) + plays(final_day, t, FSU) >= 1)
    end

    # 7. Constrained matches: these pairings occur at least once on dates 11 to 18
    for (a, b) in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]
        @constraint(model, sum(plays(d, a, b) for d in 11:final_day) >= 1)
    end

    # 8. Opponent sequences
    for t in teams
        if t != DUKE && t != UNC
            # no team plays away against UNC and Duke on two consecutive dates (either order)
            for d in 1:n_days-1
                @constraint(model, host[(d, UNC, t)] + host[(d + 1, DUKE, t)] <= 1)
                @constraint(model, host[(d, DUKE, t)] + host[(d + 1, UNC, t)] <= 1)
            end
        end
        if t != UNC && t != DUKE && t != WAKE
            # no team plays UNC, Duke and Wake on three consecutive dates, in any order and
            # whether home or away
            for d in 1:n_days-2, (a, b, c) in [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                                              (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]
                @constraint(model, plays(d, t, a) + plays(d + 1, t, b) + plays(d + 2, t, c) <= 2)
            end
        end
    end

    # 9. Other constraints
    # UNC plays its rival Duke on the last date and on date 11
    @constraint(model, plays(11, UNC, DUKE) == 1)
    @constraint(model, plays(final_day, UNC, DUKE) == 1)
    # UNC plays Clem on the second date
    @constraint(model, plays(2, UNC, CLEM) == 1)
    # Duke has a bye on date 16
    @constraint(model, bye(16, DUKE) == 1)
    # Wake does not play home on date 17
    @constraint(model, home(17, WAKE) == 0)
    # Wake has a bye on the first date
    @constraint(model, bye(1, WAKE) == 1)
    # Clem, Duke, UMD and Wake do not play away on the last date
    @constraint(model, [t in (CLEM, DUKE, UMD, WAKE)], away(final_day, t) == 0)
    # Clem, FSU, GT and Wake do not play away on the first date
    @constraint(model, [t in (CLEM, FSU, GT, WAKE)], away(1, t) == 0)
    # neither FSU nor NCSt has a bye on the last date
    @constraint(model, [t in (FSU, NCSt)], bye(final_day, t) == 0)
    # UNC does not have a bye on the first date
    @constraint(model, bye(1, UNC) == 0)

    # config[d, t] = the team that team t meets on date d (t itself on a bye), numbered from 0;
    # side[d, t] = 0 when t plays at home, 1 on a bye, 2 when away. Both are written as
    # expressions of the match variables.
    config = [sum((u - 1) * plays(d, t, u) for u in teams if u != t) + (t - 1) * bye(d, t)
              for d in days, t in teams]
    side = [1 - home(d, t) + away(d, t) for d in days, t in teams]

    return model, Dict("config" => config, "where" => side)
end
