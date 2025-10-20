import re
from .utils import logger

from binaryninja import BackgroundTaskThread, BinaryView, Logger


def update_young_and_err_regs(bv: BinaryView):
    _RenameRegsTask(bv).start()

class _RenameRegsTask(BackgroundTaskThread):
    def __init__(self, bv: BinaryView):
        super().__init__("Updating OCaml regs", True)
        self.bv = bv

    def run(self):
        try: 
            self.bv.set_analysis_hold(True)
            with self.bv.undoable_transaction():
                yng_sum = 0
                err_sum = 0

                for func in self.bv.functions:
                    yong_cnt, err_cnt = self.__update_func(func)
                    yng_sum += yong_cnt
                    err_sum += err_cnt
        finally:
            self.bv.set_analysis_hold(False)

            logger.log_info(f"Renamed {yng_sum} young ptrs")
            logger.log_info(f"Renamed {err_sum} exeption ptrs")
            # update after printing because it takes a while
            self.bv.update_analysis_and_wait()


    def __update_func(self, func):
        r14_or_r15_var = re.compile(r'^(?:r1[45](?:_\d+)?|entry_r1[45])')

        yng_cnt = yng_existing = sum(var.name.startswith("caml_young_ptr") for var in func.vars)
        err_cnt = err_existing = sum(var.name.startswith("caml_exeption_ptr") for var in func.vars)

        for var in func.vars:
            if r14_or_r15_var.match(var.name):
                if '14' in var.name:
                    var.name = f"caml_young_ptr{'' if yng_cnt == 0 else f'_{yng_cnt}'}"
                    yng_cnt += 1
                elif '15' in var.name:
                    var.name = f"caml_exeption_ptr{'' if err_cnt == 0 else f'_{err_cnt}'}"
                    err_cnt += 1

        return yng_cnt - yng_existing, err_cnt - err_existing


