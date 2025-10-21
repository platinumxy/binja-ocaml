from binaryninja import *

def update_problematic_calls(bv: BinaryView):
    
    # TODO improve the typesig  
    problems = ["caml_call_realloc_stack", "caml_call_gc"]
    void_func_type = FunctionType.create(
        None,
        [],
        calling_convention= bv.arch.calling_conventions['ocamlcall']
    )
    bv.set_analysis_hold(True)
    
    for func_name in problems:
        if func := bv.get_functions_by_name(func_name):
            for f in func:
                f.type = void_func_type

    bv.set_analysis_hold(False)
    bv.update_analysis_and_wait()