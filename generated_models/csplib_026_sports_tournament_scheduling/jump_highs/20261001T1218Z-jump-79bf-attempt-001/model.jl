# Sports tournament scheduling: n teams play over n-1 weeks, each week split into n/2
# periods with one match per period (a home team against an away team). Every team plays
# once a week, every team plays at most twice in the same period, and every team plays
# every other team.
using JuMP

function build(instance)
    n = instance["n_teams"]
    n_weeks = n - 1
    n_periods = div(n, 2)

    model = Model()

    # match[w, p, t, u] = 1 when team t is at home against team u (away) in week w, period p.
    # A team never plays itself, so only t != u gets a variable (the others are fixed to 0).
    @variable(model, match[1:n_weeks, 1:n_periods, 1:n, 1:n], Bin)
    @constraint(model, [w = 1:n_weeks, p = 1:n_periods, t = 1:n], match[w, p, t, t] == 0)

    # exactly one match is played in every (week, period) slot
    @constraint(model, [w = 1:n_weeks, p = 1:n_periods], sum(match[w, p, :, :]) == 1)

    # plays[w, p, t] = 1 when team t plays in week w, period p (as home or as away)
    plays = [sum(match[w, p, t, u] + match[w, p, u, t] for u in 1:n)
             for w in 1:n_weeks, p in 1:n_periods, t in 1:n]

    # every team plays once a week
    @constraint(model, [w = 1:n_weeks, t = 1:n], sum(plays[w, :, t]) == 1)

    # every team plays every other team (in either home/away order)
    @constraint(model, [t = 1:n-1, u = t+1:n],
                sum(match[w, p, t, u] + match[w, p, u, t]
                    for w in 1:n_weeks, p in 1:n_periods) >= 1)

    # every team plays at most twice in the same period over the tournament
    @constraint(model, [p = 1:n_periods, t = 1:n], sum(plays[:, p, t]) <= 2)

    # home[w, p] and away[w, p] = the team (numbered from 1) playing home / away in week w,
    # period p. They are bounded integer variables tied to the match indicators so that
    # enumeration cuts only these.
    @variable(model, 1 <= home[1:n_weeks, 1:n_periods] <= n, Int)
    @variable(model, 1 <= away[1:n_weeks, 1:n_periods] <= n, Int)
    @constraint(model, [w = 1:n_weeks, p = 1:n_periods],
                home[w, p] == sum(t * match[w, p, t, u] for t in 1:n, u in 1:n))
    @constraint(model, [w = 1:n_weeks, p = 1:n_periods],
                away[w, p] == sum(u * match[w, p, t, u] for t in 1:n, u in 1:n))

    return model, Dict("home" => home, "away" => away)
end
