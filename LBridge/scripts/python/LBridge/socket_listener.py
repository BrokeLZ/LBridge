import sys
import socket
import threading
import json
from .global_vars import strip_received_data
from .asset_import import import_asset
from .logging_setup import set_log


host, port = 'localhost', 24981
stop_flag = threading.Event()


def process_asset_data(data):
    try:
        data_dict = json.loads(data)
    except json.JSONDecodeError as e:
        set_log("Error parsing JSON to dictionary", exc_info=sys.exc_info())
        data_dict = None
        return
    except Exception as e:
        set_log("Unexpected error while trying to process asset data", exc_info=sys.exc_info())
        raise e

    asset_data = strip_received_data(data_dict)
    import_asset(asset_data)


def houdini_listener():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            s.listen()
            set_log(f"Houdini Listener started on {host}:{port}", "Message")
        except Exception as e:
            set_log(f"Failed to bind listener to {host}:{port}", exc_info=sys.exc_info())
            raise e

        try:
            while not stop_flag.is_set():
                try:
                    s.settimeout(1.0)
                    conn, addr = s.accept()
                    with conn:
                        buffer = ""
                        while True:
                            data = conn.recv(4096 * 2).decode("utf-8")
                            if not data:
                                break
                            buffer += data
                            try:
                                data_dict = json.loads(buffer)
                                process_asset_data(buffer)
                                buffer = ""
                            except json.JSONDecodeError:
                                continue
                except socket.timeout:
                    continue
        except Exception as e:
            set_log("Error during data reception or processing", exc_info=sys.exc_info())


def run_listener():
    try:
        stop_flag.clear()
        listener_thread = threading.Thread(target=houdini_listener, daemon=True)
        listener_thread.start()
    except Exception as e:
        set_log("Error running the Houdini Listener", exc_info=sys.exc_info())
        raise e

def stop_listener():
    try:
        stop_flag.set()
        set_log("Houdini Listener stopped`\n\n\n\n\n\n", "Message")
    except Exception as e:
        set_log("Error stopping the Houdini Listener", exc_info=sys.exc_info())
