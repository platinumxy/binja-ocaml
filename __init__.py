from binaryninja import *

from .src import regs, utils, calling_convention, function_cleanup

PluginCommand.register(
    "OCaml Helper\\Update Young and Exception Regs",
    "Rename r14 and r15 vars to caml_exeption_ptr and caml_young_ptr respectively",
    regs.update_young_and_err_regs,
    utils.arch_is_ocaml_amd64
)

PluginCommand.register(
    "OCaml Helper\\Convert to OCaml AMD64 Calling Convention",
    "Set the calling convention of functions without one to OCaml AMD64",
    calling_convention.convert_to_ocaml_call_amd64,
    utils.arch_is_ocaml_amd64
)

PluginCommand.register(
    "OCaml Helper\\Update Problematic Calls",
    "Cleans up GC and stack realloc calls",
    function_cleanup.update_problematic_calls,
    utils.arch_is_ocaml_amd64
)

PluginCommand.register(
    "OCaml Helper\\Toggle\\Ignore caml/ocaml mentions when detecting OCaml bins",
    "Ignore caml/ocaml mentions when detecting OCaml bins",
    utils.toggle_ignore_caml_mentions
)
