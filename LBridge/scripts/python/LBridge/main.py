import sys

import hou
from .import_options_window import init_window
from .socket_listener import run_listener
from.logging_setup import set_log

def main():
    try:
        run_listener()
        init_window()
    except Exception as e:
        set_log("An error occurred in main", exc_info=sys.exc_info())
        raise e



