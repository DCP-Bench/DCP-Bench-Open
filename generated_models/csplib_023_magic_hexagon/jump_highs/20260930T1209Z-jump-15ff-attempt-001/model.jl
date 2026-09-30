# Magic hexagon: place the numbers 1..19 in the 19 cells of a hexagon (rows of
# 3, 4, 5, 4 and 3 cells) so that each of the 15 lines adds up to the magic sum.
using JuMP

function build(instance)
    ncells = instance["NUM_CELLS"]
    magic = instance["MAGIC_SUM"]
    # Cells are numbered row by row from 1:
    #        1  2  3
    #      4  5  6  7
    #    8  9 10 11 12
    #     13 14 15 16
    #       17 18 19
    # The lines are the five rows and the five lines in each diagonal direction.
    lines = [[1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11, 12], [13, 14, 15, 16], [17, 18, 19],
             [1, 4, 8], [2, 5, 9, 13], [3, 6, 10, 14, 17], [7, 11, 15, 18], [12, 16, 19],
             [3, 7, 12], [2, 6, 11, 16], [1, 5, 10, 15, 19], [4, 9, 14, 18], [8, 13, 17]]
    model = Model()
    @variable(model, 1 <= LD[1:ncells] <= ncells, Int)
    @constraint(model, LD in MOI.AllDifferent(ncells))
    @constraint(model, [line in lines], sum(LD[c] for c in line) == magic)
    return model, Dict("LD" => LD)
end
