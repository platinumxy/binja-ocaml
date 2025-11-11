import re

from binaryninja import BinaryView

from .utils import logger, background_wrapper


@background_wrapper("Updating OCaml young and exception regs")
def update_young_and_err_regs(bv: BinaryView):
    with bv.undoable_transaction():  # type: ignore
        yng_sum = 0
        err_sum = 0

        for func in bv.functions:
            cnts = __update_func(func)
            yng_sum += cnts[0]
            err_sum += cnts[1]

    logger.log_info(f"Renamed {yng_sum} young ptrs")
    logger.log_info(f"Renamed {err_sum} exception ptrs")


def __update_func(func):
    r14_or_r15_var = re.compile(r"^(?:r1[45](?:_\d+)?|entry_r1[45])")

    yng_cnt = yng_exist = sum(var.name.startswith("young_ptr") for var in func.vars)
    err_cnt = err_exist = sum(var.name.startswith("caml_exception_ptr") for var in func.vars)

    for var in func.vars:
        if r14_or_r15_var.match(var.name):
            if "15" in var.name:
                var.name = f"young_ptr{'' if yng_cnt == 0 else f'_{yng_cnt}'}"
                yng_cnt += 1
            elif "14" in var.name:
                var.name = f"caml_exception_ptr{'' if err_cnt == 0 else f'_{err_cnt}'}"
                err_cnt += 1

    return yng_cnt - yng_exist, err_cnt - err_exist
