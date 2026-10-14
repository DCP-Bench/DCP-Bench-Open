import json, importlib.util
spec = importlib.util.spec_from_file_location("m", "/probe/knap_model.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
inst = json.load(open("/probe/knap.json"))
for gap in (None, 0):
    model, out = m.build(inst)
    model.Params.OutputFlag = 0; model.Params.Threads = 1
    if gap is not None: model.Params.MIPGap = gap
    model.optimize()
    print("MIPGap", "default" if gap is None else gap, "status", model.Status, "obj", round(model.ObjVal), "bound", round(model.ObjBound))
