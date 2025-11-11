from typing import Tuple, List

from binaryninja import (
    BinaryView,
    Function,
    FunctionType,
    Type,
    Variable,
    VariableSourceType,
)

from .utils import logger, background_wrapper, pause_analysis

# called by caml_call_realloc_stack and caml_call_gc
AMD64_SAVE_ALL_REGS = bytes.fromhex("4d895f584d8b1f4d895e5049890749895f0849897f10498977184989572049894f284d8947304d894f384d8967404d896f484d89575049896f60f2410f114768f2410f114f70f2410f115778f2410f119f80000000f2410f11a788000000f2410f11af90000000f2410f11b798000000f2410f11bfa0000000f2450f1187a8000000f2450f118fb0000000f2450f1197b8000000f2450f119fc0000000f2450f11a7c8000000f2450f11afd0000000f2450f11b7d8000000f2450f11bfe0000000")
AMD64_RESTORE_ALL_REGS = bytes.fromhex("4d891f4d897e50498b5f08498b7f10498b7718498b5720498b4f284d8b47304d8b4f384d8b67404d8b6f484d8b57504d8b5f58498b6f60f2410f104768f2410f104f70f2410f105778f2410f109f80000000f2410f10a788000000f2410f10af90000000f2410f10b798000000f2410f10bfa0000000f2450f1087a8000000f2450f108fb0000000f2450f1097b8000000f2450f109fc0000000f2450f10a7c8000000f2450f10afd0000000f2450f10b7d8000000f2450f10bfe00000004d8b7e08")
AMD54_SAVE_XMM_REGS = bytes.fromhex("4881ec80000000f20f110424f20f114c2408f20f11542410f20f115c2418f20f11642420f20f116c2428f20f11742430f20f117c2438f2440f11442440f2440f114c2448f2440f11542450f2440f115c2458f2440f11642460f2440f116c2468f2440f11742470f2440f117c2478")

@background_wrapper("Update problematic OCaml runtime function types when symbols are present")
def auto_update_problematic_calls(bv: BinaryView):

    void_func_type = FunctionType.create( # TODO improve the typesig
        None, [], calling_convention=bv.arch.calling_conventions["ocamlcall"]  # type: ignore
    )

    with pause_analysis(bv):
        PROBLEMS = ["caml_call_realloc_stack", "caml_call_gc"]
        found = 0
        for func_name in PROBLEMS:
            if func := bv.get_functions_by_name(func_name):
                for f in func:
                    f.type = void_func_type
            found += 1

    if found != len(PROBLEMS):
        logger.log_warn("Could not find symbols for some OCaml runtime functions; Consider running auto detect.")

@background_wrapper("Manually detect and update OCaml runtime functions")
def detect_ocaml_runtime_functions(bv: BinaryView):
    funcReStack, fucnCallGC = find_realloc_stack_and_call_gc(bv)

    
    with pause_analysis(bv):
        if fucnCallGC is not None:
            logger.log_info(f"Detected caml_call_gc at {hex(fucnCallGC.start)}")
            fucnCallGC.name = "caml_call_gc"
            fucnCallGC.set_auto_return_type(Type.void())
            fucnCallGC.set_auto_calling_convention(bv.arch.calling_conventions["ocamlcall"])  # type: ignore
            fucnCallGC.set_auto_parameter_vars([])
        else: 
            logger.log_warn("Could not detect caml_call_gc function")

        if funcReStack is not None:
            logger.log_info(f"Detected caml_call_realloc_stack at {hex(funcReStack.start)}")
            funcReStack.name = "caml_call_realloc_stack"
            funcReStack.set_auto_return_type(Type.bool())
            funcReStack.set_auto_return_regs(["rax"])  # type: ignore
            funcReStack.set_auto_calling_convention(bv.arch.calling_conventions["ocamlcall"]) # type: ignore
            stack_param = Variable(funcReStack, VariableSourceType.StackVariableSourceType, 8, 8)

            # stack_param.name = "count"  # whyd this crash :sob:
            funcReStack.set_auto_parameter_vars([stack_param])
        else:
            logger.log_warn("Could not detect caml_call_realloc_stack function")




def find_all_patterns(bv: BinaryView, pat: bytes) -> List[Function]:
    results = []
    offset = 0
    addr = bv.find_next_data(offset, pat)

    while addr is not None:
        results.append(addr)
        offset = addr + len(pat)
        addr = bv.find_next_data(offset, pat)

    return [
        bv.get_functions_containing(addr)[0]
        for addr in results if bv.get_functions_containing(addr)
    ]


def find_realloc_stack_and_call_gc(bv: BinaryView) -> Tuple[Function | None, Function | None]:
    save_regs = find_all_patterns(bv, AMD64_SAVE_ALL_REGS)
    restore_regs = find_all_patterns(bv, AMD64_RESTORE_ALL_REGS)

    # Easy cheat code is caml_call_realloc_stack as it generate calls to restore_regs
    if len(restore_regs) == 3 and list(set(restore_regs)) != restore_regs:
        func1, func2 = list(set(restore_regs))
        if restore_regs.count(func1) == 2:
            return func1, func2
        return func2, func1
    # Todo impl
    return None, None

