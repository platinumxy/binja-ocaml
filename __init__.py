from binaryninja import *

from .src import regs, utils, calling_convention, function_detection

PluginCommand.register(
    "OCaml Helper\\Update Young and Exception Regs",
    "Rename r14 and r15 vars to caml_exeption_ptr and caml_young_ptr respectively",
    regs.update_young_and_err_regs,
    utils.is_ocaml_amd64_bin,
)

PluginCommand.register(
    "OCaml Helper\\Convert to OCaml AMD64 Calling Convention",
    "Set the calling convention of functions without one to OCaml AMD64",
    calling_convention.convert_to_ocaml_call_amd64,
    utils.is_ocaml_amd64_bin,
)

PluginCommand.register(
    "OCaml Helper\\Problematic Calls\\Fix types based of symbols",
    "Cleans up GC and stack realloc calls",
    function_detection.auto_update_problematic_calls,
    utils.is_ocaml_amd64_bin,
)

PluginCommand.register(
    "OCaml Helper\\Problematic Calls\\Try detect problematic calls",
    "Cleans up GC and stack realloc calls",
    function_detection.detect_ocaml_runtime_functions,
    utils.is_ocaml_amd64_bin,
)


PluginCommand.register(
    "OCaml Helper\\Toggle\\Ignore caml/ocaml mentions when detecting OCaml bins",
    "Ignore caml/ocaml mentions when detecting OCaml bins",
    utils.toggle_ignore_caml_mentions,
)
