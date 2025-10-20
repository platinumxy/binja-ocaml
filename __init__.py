from binaryninja import *

from .src import regs, utils


PluginCommand.register(
    "OCaml Helper\\Update Young and Exception Regs",
    "Rename r14 and r15 vars to caml_exeption_ptr and caml_young_ptr respectively",
    regs.update_young_and_err_regs,
    utils.arch_is_amd64
)

