from binaryninja import *

def arch_is_amd64(bv:BinaryView) -> bool:
    
    return bv.arch and bv.arch.name == "x86_64"


logger = Logger(session_id=0, logger_name="OCaml Helper")