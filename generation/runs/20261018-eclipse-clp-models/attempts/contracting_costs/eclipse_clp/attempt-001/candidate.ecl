% contracting_costs: a contractor pays pairs of workers for their services.
% Find what each of the six men (paper hanger, painter, plumber, electrician,
% carpenter, mason) charges for his services, in dollars.
:- lib(ic).

model(_Instance, Vars, Outputs) :-
    Vars = [PaperHanger, Painter, Plumber, Electrician, Carpenter, Mason],
    % each charge is a whole number of dollars, at most the largest pair total (5,300)
    Vars :: 0..5300,
    % $1,100 to the paper hanger and the painter
    PaperHanger + Painter #= 1100,
    % $1,700 to the painter and plumber
    Painter + Plumber #= 1700,
    % $1,100 to the plumber and electrician
    Plumber + Electrician #= 1100,
    % $3,300 to the electrician and carpenter
    Electrician + Carpenter #= 3300,
    % $5,300 to the carpenter and mason
    Carpenter + Mason #= 5300,
    % $3,200 to the mason and painter
    Mason + Painter #= 3200,
    Outputs = [paper_hanger-PaperHanger, painter-Painter, plumber-Plumber,
               electrician-Electrician, carpenter-Carpenter, mason-Mason].
