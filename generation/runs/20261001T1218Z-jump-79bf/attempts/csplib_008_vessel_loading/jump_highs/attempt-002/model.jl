# Vessel loading: place rectangular containers on a rectangular deck, sides parallel to
# the deck, in a single layer. Containers may not overlap, and containers of certain
# classes must be kept a minimum distance apart. Decide whether all can be positioned.
using JuMP

function build(instance)
    deck_width = instance["deck_width"]
    deck_length = instance["deck_length"]
    n = instance["n_containers"]
    width = instance["width"]           # width of each container
    length_ = instance["length"]        # length of each container
    classes = instance["classes"]       # class (1-based) of each container
    separation = instance["separation"] # minimum distance between two classes

    model = Model()

    # A container is laid either as given (width along the deck width, length along the
    # deck length) or turned by 90 degrees; a square has only one orientation.
    # placements[i] lists every way to put container i on the deck: (size along the deck
    # width, size along the deck length, left edge, bottom edge), with the container
    # inside the deck.
    orientations(i) = width[i] == length_[i] ? [(width[i], length_[i])] :
                      [(width[i], length_[i]), (length_[i], width[i])]
    placements = [[(w, h, x, y) for (w, h) in orientations(i)
                   for x in 0:deck_width-w for y in 0:deck_length-h] for i in 1:n]

    # put[i][k] = 1 when container i takes its k-th placement; each container is placed once
    put = [@variable(model, [1:length(placements[i])], Bin) for i in 1:n]
    @constraint(model, [i = 1:n], sum(put[i]) == 1)

    # The deck is a grid of unit cells (cx, cy), 0-based. cells_of(i, s) maps each cell to
    # the placements of container i whose rectangle, grown by s on every side, covers it.
    # With s = 0 these are the cells the container occupies.
    function cells_of(i, s)
        covering = Dict{Tuple{Int,Int},Vector{VariableRef}}()
        for (k, (w, h, x, y)) in enumerate(placements[i])
            for cx in max(0, x - s):min(deck_width - 1, x + w - 1 + s),
                cy in max(0, y - s):min(deck_length - 1, y + h - 1 + s)
                push!(get!(covering, (cx, cy), VariableRef[]), put[i][k])
            end
        end
        return covering
    end
    occupied = [cells_of(i, 0) for i in 1:n]

    # No overlap: a cell of the deck belongs to at most one container. Using cells makes
    # the linear relaxation much tighter than comparing coordinates with big-M constraints.
    for cx in 0:deck_width-1, cy in 0:deck_length-1
        users = [v for i in 1:n for v in get(occupied[i], (cx, cy), VariableRef[])]
        length(users) > 1 && @constraint(model, sum(users) <= 1)
    end

    # Class separation: container y must be at least s from every earlier container x, where
    # s is the separation between their classes. That means x occupies no cell of y grown by
    # s on every side. For each y and each distance s > 0, the earlier containers that must
    # keep distance s together occupy a cell at most once, and not together with y's grown
    # rectangle.
    for y in 2:n
        for s in sort(unique(separation[classes[x]][classes[y]] for x in 1:y-1))
            s > 0 || continue
            keep_apart = [x for x in 1:y-1 if separation[classes[x]][classes[y]] == s]
            grown = cells_of(y, s)
            for cx in 0:deck_width-1, cy in 0:deck_length-1
                near = get(grown, (cx, cy), VariableRef[])
                isempty(near) && continue
                taken = [v for x in keep_apart for v in get(occupied[x], (cx, cy), VariableRef[])]
                isempty(taken) || @constraint(model, sum(taken) + sum(near) <= 1)
            end
        end
    end

    # left[i] .. right[i] and bottom[i] .. top[i] = the space container i occupies on the
    # deck (declared outputs), read off the chosen placement
    left = [sum(p[3] * put[i][k] for (k, p) in enumerate(placements[i])) for i in 1:n]
    right = [sum((p[3] + p[1]) * put[i][k] for (k, p) in enumerate(placements[i])) for i in 1:n]
    bottom = [sum(p[4] * put[i][k] for (k, p) in enumerate(placements[i])) for i in 1:n]
    top = [sum((p[4] + p[2]) * put[i][k] for (k, p) in enumerate(placements[i])) for i in 1:n]

    return model, Dict("left" => left, "right" => right, "top" => top, "bottom" => bottom)
end
