# Exodus: five children (Bernice, Carl, Debby, Sammy, Ted) each tell a different part of the
# Exodus story, are a different age (3, 5, 7, 8, 10) and come from a different country
# (Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen). Match ages, children, countries and
# stories using the five clues.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 5
    age_years = [3, 5, 7, 8, 10]   # the five ages, in the order the problem lists them
    # position of each entity inside its category, in the order the problem lists them
    bernice, carl, debby, sammy, ted = 1, 2, 3, 4, 5
    ethiopia, kazakhstan, lithuania, morocco, yemen = 1, 2, 3, 4, 5
    burning_bush, captivity, moses_youth, passover, ten_commandments = 1, 2, 3, 4, 5
    # the four categories, as the first index of the arrays below
    AGES, CHILDREN, COUNTRIES, STORIES = 1, 2, 3, 4

    model = Model()

    # Entities with the same number (1..5) belong to the same child. at[c, k, s] = 1 when entity
    # k of category c is assigned to child number s; slot[c, k] is that number, which is what
    # the problem asks us to print. All entities of a category get different numbers.
    @variable(model, at[1:4, 1:n, 1:n], Bin)
    @constraint(model, [c = 1:4, k = 1:n], sum(at[c, k, :]) == 1)
    @constraint(model, [c = 1:4, s = 1:n], sum(at[c, :, s]) == 1)
    @variable(model, 1 <= slot[1:4, 1:n] <= n, Int)
    @constraint(model, [c = 1:4, k = 1:n], slot[c, k] == sum(s * at[c, k, s] for s in 1:n))

    # age_of_child[s] = the age in years of child number s
    age_of_child = [sum(age_years[k] * at[AGES, k, s] for k in 1:n) for s in 1:n]

    # years(c, e) = the age in years of the child that entity e of category c belongs to,
    # i.e. sum over s of at[c, e, s] * age_of_child[s]. That is a product of a binary and a
    # bounded quantity (0..10), linearised with one helper per child.
    function years(c, e)
        z = @variable(model, [1:n], lower_bound = 0, upper_bound = 10)
        for s in 1:n
            @constraint(model, z[s] <= 10 * at[c, e, s])
            @constraint(model, z[s] <= age_of_child[s])
            @constraint(model, z[s] >= age_of_child[s] - 10 * (1 - at[c, e, s]))
        end
        return sum(z)
    end

    # 1. Debby's family is from Lithuania
    @constraint(model, slot[CHILDREN, debby] == slot[COUNTRIES, lithuania])
    # 2. The child who told the story of the Passover is two years older than Bernice
    @constraint(model, years(STORIES, passover) == years(CHILDREN, bernice) + 2)
    # 3. The child whose family is from Yemen is younger than the child from the Ethiopian family
    #    (ages are whole years, so younger means at least one year less)
    @constraint(model, years(COUNTRIES, yemen) + 1 <= years(COUNTRIES, ethiopia))
    # 4. The child from the Moroccan family is three years older than Ted
    @constraint(model, years(COUNTRIES, morocco) == years(CHILDREN, ted) + 3)
    # 5. Sammy is three years older than the child who told the story of Moses's youth
    @constraint(model, years(CHILDREN, sammy) == years(STORIES, moses_youth) + 3)

    return model, Dict("ages" => slot[AGES, :], "children" => slot[CHILDREN, :],
                       "countries" => slot[COUNTRIES, :], "stories" => slot[STORIES, :])
end
