from binaryninja import BinaryView, BackgroundTaskThread, Logger
from typing import Callable

logger = Logger(session_id=0, logger_name="OCaml Helper")
IGNORE_CAML_MENTIONS = False

def pause_analysis(bv: BinaryView):
    class PauseAnalysis:    
        def __init__(self, bv: BinaryView):
            self.bv = bv

        def __enter__(self):
            self.bv.set_analysis_hold(True)

        def __exit__(self, exc_type, exc_value, traceback):
            self.bv.set_analysis_hold(False)
            self.bv.update_analysis_and_wait()
    return PauseAnalysis(bv)

def background_wrapper(task_name: str) -> Callable:
    """Decorator factory that wraps a function to run in a background task."""

    def decorator(func: Callable[[BinaryView], None]) -> Callable[[BinaryView], None]:
        class _BackgroundTask(BackgroundTaskThread):
            def __init__(self, bv: BinaryView):
                super().__init__(task_name, True)
                self.bv = bv

            def run(self):
                try:
                    self.bv.set_analysis_hold(True)
                    with self.bv.undoable_transaction():  # type: ignore
                        func(self.bv)
                finally:
                    self.bv.set_analysis_hold(False)
                    self.bv.update_analysis_and_wait()

        return lambda bv: _BackgroundTask(bv).start()

    return decorator


def toggle_ignore_caml_mentions(bv: BinaryView):
    global IGNORE_CAML_MENTIONS
    
    IGNORE_CAML_MENTIONS = not IGNORE_CAML_MENTIONS
    bv.update_analysis_and_wait() # annoyingly you've got to force an update


def is_ocaml_amd64_bin(bv: BinaryView) -> bool:
    if bv.arch is None or bv.arch.name != "x86_64":
        return False    
    return ((string_cnt_in_bin(bv, b"caml") + string_cnt_in_bin(bv, b"ocaml")) > 5  # arbitrary threshold
    ) or IGNORE_CAML_MENTIONS
    


def string_cnt_in_bin(bv: BinaryView, string: bytes) -> int:
    return sum(bv.read(segment.start, segment.length).count(string) for segment in bv.segments)
