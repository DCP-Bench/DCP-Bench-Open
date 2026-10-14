# Movie scheduling: accept as many movie offers as possible, where two accepted
# movies never have overlapping filming periods (first to last day, inclusive).
using JuMP

function build(instance)
    movies = instance["movies"]    # [title, first day, last day]
    n = length(movies)
    model = Model()
    @variable(model, selected[1:n], Bin)
    for i in 1:n-1, j in i+1:n
        if movies[i][3] >= movies[j][2] && movies[j][3] >= movies[i][2]
            @constraint(model, selected[i] + selected[j] <= 1)
        end
    end
    @objective(model, Max, sum(selected))
    return model, Dict("selected_movies" => selected)
end
