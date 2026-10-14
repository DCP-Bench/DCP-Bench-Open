# Finding celebrities: at a party, graph[i][j] = 1 when person i knows person j. A
# celebrity is known by everybody and only knows other celebrities; at least one
# celebrity is present. Decide who the celebrities are.
using JuMP

function build(instance)
    graph = instance["graph"]   # graph[i][j] = 1 when person i knows person j
    n = length(graph)

    model = Model()

    # celebrities[i] = 1 when person i is a celebrity (declared output)
    @variable(model, celebrities[1:n], Bin)

    # num_celebrities is how many celebrities there are, at least one and at most n.
    # is_count[v] = 1 when there are exactly v of them, so that "person i knows exactly
    # num_celebrities people" can be tested against the constant number of people i knows.
    is_count = @variable(model, [1:n], Bin)
    @constraint(model, sum(is_count) == 1)
    @constraint(model, sum(celebrities) == sum(v * is_count[v] for v in 1:n))

    # Everyone knows a celebrity, and a celebrity only knows other celebrities, so a
    # celebrity is known by all n persons and knows exactly num_celebrities persons.
    # Both counts come from the graph, so each person is either ruled out as a celebrity
    # or is one exactly when the number of celebrities equals the number they know.
    for i in 1:n
        known_by = sum(graph[j][i] for j in 1:n)   # people who know i
        knows = sum(graph[i][j] for j in 1:n)      # people i knows
        if known_by == n && 1 <= knows <= n
            @constraint(model, celebrities[i] == is_count[knows])
        else
            @constraint(model, celebrities[i] == 0)
        end
    end

    return model, Dict("celebrities" => celebrities)
end
