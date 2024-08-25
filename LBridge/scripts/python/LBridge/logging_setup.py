import hou
import os
import traceback


def fix_path(path, sep="/"):
    _path = path.replace("\\", "/")
    _path = _path.replace("\\\\", "/")
    _path = _path.replace("//", "/")

    _path = _path.replace("x03d/x03d", "3d/3d")
    _path = _path.replace("x03dplant/x03dplant", "3dplant/3dplant")

    if _path.endswith("/"):
        _path = _path[:-1]

    fixed_path = _path.replace("/", sep)

    return fixed_path


source_name = "LBridge_logger"
script_dir = os.path.dirname(__file__)
_log_dir = os.path.dirname(script_dir)
_log_dir = os.path.dirname(_log_dir)
_log_dir = os.path.dirname(_log_dir)
log_file_path = fix_path(os.path.join(_log_dir, "logs", "logfile.log"))
max_log_size = 5 * 1024 * 1024
backupt_count = 3


def rotate_logs():
    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) >= max_log_size:
        for i in range(backupt_count - 1, 0, -1):
            old_log = f"{log_file_path}.{i}"
            new_log = f"{log_file_path}.{i+1}"
            if os.path.exists(old_log):
                os.rename(old_log, new_log)

        os.rename(log_file_path, f"{log_file_path}.1")

        open(log_file_path, "w").close()


try:
    hou.logging.createSource(source_name)
except Exception as e:
    print(f"Failed to create logging source: {e}")

rotate_logs()

try:
    sink = hou.logging.FileSink(log_file_path)
    sink.connect(source_name)
except Exception as e:
    print(f"Failed to set up logging: {e}")


LOGGER_SOURCE_NAME = source_name

def set_log(message, severity="Error", exc_info=False):
    try:
        severity_type = getattr(hou.severityType, severity, hou.severityType.Message)
        log_message = message

        if exc_info:
            exc_type, exc_value, exc_tb = exc_info
            traceback_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            log_message = f"{severity}: {message}:\n\nException traceback:\n{traceback_str}"

        entry = hou.logging.LogEntry(message=log_message, severity=severity_type)
        hou.logging.log(entry, source_name=LOGGER_SOURCE_NAME)
    except Exception as e:
        print(f"Logging failed: {e}")




