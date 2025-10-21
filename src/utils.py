from binaryninja import *


IGNORE_CAML_MENTIONS = False
def toggle_ignore_caml_mentions(bv:BinaryView):
    global IGNORE_CAML_MENTIONS
    IGNORE_CAML_MENTIONS = not IGNORE_CAML_MENTIONS

    # annoyingly you've got to force an update
    bv.update_analysis_and_wait()

def arch_is_ocaml_amd64(bv:BinaryView) -> bool:
    if (not bv.arch) or bv.arch.name != "x86_64":
        return False
    
    
    if IGNORE_CAML_MENTIONS:
        return True

    # Check weve ocaml strings in rodata
    caml_cnt = string_cnt_in_bin(bv, b"caml")
    ocaml_cnt = string_cnt_in_bin(bv, b"ocaml")
    return (caml_cnt + ocaml_cnt) > 5 # arbitrary threshold


def string_cnt_in_bin(bv:BinaryView, string: bytes) -> int:
    return sum(bv.read(segment.start, segment.length).count(string) for segment in bv.segments)

logger = Logger(session_id=0, logger_name="OCaml Helper")