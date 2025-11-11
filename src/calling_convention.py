from binaryninja import *
from .utils import background_wrapper


@background_wrapper("Converting to OCaml AMD64 calling convention")
def convert_to_ocaml_call_amd64(bv: BinaryView):
    func_count = 0
    for func in bv.functions:
        func.calling_convention = ocaml_call_amd64
        func_count += 1
    logger.log_info(f"Set OCaml AMD64 calling convention on {func_count} functions")


# r14 = caml_exception_ptr
# r15 = caml_young_ptr
class OCamlCallAMD64(CallingConvention):
    name = "ocamlcall"
    # OCaml's native AMD64 calling convention (see [asmcomp/amd64/proc.ml](https://github.com/ocaml/ocaml/blob/trunk/asmcomp/amd64/proc.ml)):
    # - integer args: rax, rbx, rdi, rsi, rdx, rcx, r8, r9, r12, r13
    # - float args: xmm0 .. xmm9
    # - r14, r15 used as young ptr and exception ptr

    int_arg_regs = [
        "rax",
        "rbx",
        "rdi",
        "rsi",
        "rdx",
        "rcx",
        "r8",
        "r9",
        "r12",
        "r13",
    ]

    float_arg_regs = [
        "xmm0",
        "xmm1",
        "xmm2",
        "xmm3",
        "xmm4",
        "xmm5",
        "xmm6",
        "xmm7",
        "xmm8",
        "xmm9",
    ]
    # - r10, r11 may be clobbered by PLT/externals see https://github.com/ocaml/ocaml/blob/413eb9098cbb872da57fa0fd63748da15725fec8/asmcomp/amd64/proc.ml#L67
    plt_volatile_regs = ["r10", "r11"]

    caller_saved_regs = int_arg_regs + float_arg_regs + plt_volatile_regs

    callee_saved_regs = []

    arg_regs_share_index = False
    arg_regs_for_varargs = True
    stack_reserved_for_arg_regs = False
    stack_adjusted_on_return = False

    int_return_reg = "rax"
    high_int_return_reg = None
    float_return_reg = "xmm0"

    # I think this is the proper usage
    global_pointer_reg = "r15"
    implicitly_defined_regs = ["r14", "r15"]

    eligible_for_heuristics = False


ocaml_call_amd64 = OCamlCallAMD64(arch=Architecture["x86_64"], name="ocamlcall")
Architecture["x86_64"].register_calling_convention(ocaml_call_amd64)
