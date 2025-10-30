from binaryninja import *


def convert_to_ocaml_call_amd64(bv: BinaryView):
    _ConvertToOCamlCallAMD64Task(bv).start()


class _ConvertToOCamlCallAMD64Task(BackgroundTaskThread):
    def __init__(self, bv: BinaryView):
        super().__init__("Setting OCaml AMD64 calling convention", True)
        self.bv = bv

    def run(self):
        try:
            self.bv.set_analysis_hold(True)
            with self.bv.undoable_transaction():
                func_count = 0
                for func in self.bv.functions:
                    func.calling_convention = ocaml_call_amd64
                    func_count += 1
        finally:
            self.bv.set_analysis_hold(False)

            logger.log_info(
                f"Set OCaml AMD64 calling convention on {func_count} functions"
            )
            self.bv.update_analysis_and_wait()


# r14 = caml_exeption_ptr
# r15 = caml_young_ptr
reg_map = {
    "rax": 0, "rbx": 1, "rdi": 2, "rsi": 3,  "rdx": 4, "rcx": 5, "r8": 6, "r9": 7,
    "r12": 8, "r13": 9, "r10": 10, "r11": 11, "rbp": 12, "r14": 13, "r15": 14, "xmm0": 100,
    "xmm1": 101, "xmm2": 102, "xmm3": 103, "xmm4": 104, "xmm5": 105, "xmm6": 106, "xmm7": 107, "xmm8": 108,
    "xmm9": 109, "xmm10": 110, "xmm11": 111, "xmm12": 112, "xmm13": 113, "xmm14": 114, "xmm15": 115
}


class OCamlCallAMD64(CallingConvention):
    name = "ocamlcall"
    # OCaml's native AMD64 calling convention (see [asmcomp/amd64/proc.ml](https://github.com/ocaml/ocaml/blob/trunk/asmcomp/amd64/proc.ml)):
    # - integer args: rax, rbx, rdi, rsi, rdx, rcx, r8, r9, r12, r13
    # - float args: xmm0 .. xmm9
    # - r14, r15 used as young ptr and exception ptr

    int_arg_regs = [
        "rax", "rbx", "rdi", "rsi", "rdx", "rcx", "r8", "r9", "r12", "r13",
    ]

    float_arg_regs = [
        "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7",
        "xmm8", "xmm9",
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


ocaml_call_amd64 = OCamlCallAMD64(
    arch=Architecture["x86_64"], name="ocamlcall")
Architecture["x86_64"].register_calling_convention(ocaml_call_amd64)
