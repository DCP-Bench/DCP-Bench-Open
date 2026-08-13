from swiglpk import (
    GLP_DB,
    GLP_FEAS,
    GLP_FX,
    GLP_IV,
    GLP_MIN,
    GLP_MSG_OFF,
    GLP_ON,
    GLP_OPT,
    doubleArray,
    glp_add_cols,
    glp_add_rows,
    glp_create_prob,
    glp_delete_prob,
    glp_init_iocp,
    glp_intopt,
    glp_iocp,
    glp_load_matrix,
    glp_mip_col_val,
    glp_mip_status,
    glp_set_col_bnds,
    glp_set_col_kind,
    glp_set_col_name,
    glp_set_obj_dir,
    glp_set_row_bnds,
    intArray,
)
import json

lp = glp_create_prob()
glp_set_obj_dir(lp, GLP_MIN)
glp_add_cols(lp, 3)
for j, name in enumerate(("men", "women", "children"), start=1):
    glp_set_col_name(lp, j, name)
    glp_set_col_kind(lp, j, GLP_IV)
    glp_set_col_bnds(lp, j, GLP_DB, 0.0, 100.0)

glp_add_rows(lp, 3)
# 100 people in total
glp_set_row_bnds(lp, 1, GLP_FX, 100.0, 100.0)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
glp_set_row_bnds(lp, 2, GLP_FX, 200.0, 200.0)
# Five times as many women as men
glp_set_row_bnds(lp, 3, GLP_FX, 0.0, 0.0)

nnz = 8
ia, ja, ar = intArray(nnz + 1), intArray(nnz + 1), doubleArray(nnz + 1)
entries = (
    (1, 1, 1.0), (1, 2, 1.0), (1, 3, 1.0),
    (2, 1, 6.0), (2, 2, 4.0), (2, 3, 1.0),
    (3, 1, -5.0), (3, 2, 1.0),
)
for k, (row, col, val) in enumerate(entries, start=1):
    ia[k], ja[k], ar[k] = row, col, val
glp_load_matrix(lp, nnz, ia, ja, ar)

iocp = glp_iocp()
glp_init_iocp(iocp)
iocp.presolve = GLP_ON
iocp.msg_lev = GLP_MSG_OFF
glp_intopt(lp, iocp)
if glp_mip_status(lp) not in (GLP_OPT, GLP_FEAS):
    glp_delete_prob(lp)
    raise SystemExit("No solution found.")

print(json.dumps({
    "men": int(round(glp_mip_col_val(lp, 1))),
    "women": int(round(glp_mip_col_val(lp, 2))),
    "children": int(round(glp_mip_col_val(lp, 3))),
}))
glp_delete_prob(lp)
