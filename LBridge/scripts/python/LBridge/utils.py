import os
import ast
import platform
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from .logging_setup import set_log


def get_executable(name):
    if platform.system() == "Windows":
        return f"{name}.exe"
    else:
        return name


def fix_path(path, sep="/"):
    try:
        _path = path.replace("\\", "/")
        _path = _path.replace("\\\\", "/")
        _path = _path.replace("//", "/")

        _path = _path.replace("x03d/x03d", "3d/3d")
        _path = _path.replace("x03dplant/x03dplant", "3dplant/3dplant")

        if _path.endswith("/"):
            _path = _path[:-1]

        fixed_path = _path.replace("/", sep)

        return fixed_path
    except Exception as e:
        set_log("Error fixing path", exc_info=sys.exc_info())
        raise e


def fix_escape_chars(string):
    try:
        fixed_string = str(string).encode("unicode_escape").decode("utf-8")
        return fixed_string
    except Exception as e:
        set_log("Error fixing escape characters", exc_info=sys.exc_info())
        raise e


def convert_tex(old_file, new_file, in_colorspace, out_colorspace):
    try:
        houdini_root = os.environ.get("HFS")
        imaketx_path = os.path.join(houdini_root, "bin", get_executable("imaketx"))

        arguments = [
            imaketx_path,
            "-m", "ocio",
            "-c", f"{in_colorspace}", f"{out_colorspace}",
            old_file,
            new_file
        ]

        subprocess.run(arguments, check=True)

    except Exception as e:
        set_log("Error converting texture formats", exc_info=sys.exc_info())
        raise e


def convert_textures_in_parallel(textures_data, max_workers=5):
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_texture = {}

            # Loop through textures_data and submit tasks
            for name, data in textures_data.items():
                set_log(f"Converting old file: {data[0]}")  # Debugging: print old file name

                future = executor.submit(
                    convert_tex,
                    data[0],  # old_file
                    data[1],  # new_file
                    data[2],  # in_colorspace
                    data[3]   # out_colorspace
                )

                future_to_texture[future] = name

            for future in as_completed(future_to_texture):
                texture_name = future_to_texture[future]
                try:
                    future.result()
                except Exception as e:
                    set_log(f"Conversion failed for {texture_name}", exc_info=sys.exc_info())
                    raise e
    except Exception as e:
        set_log("error batch converting texture format", exc_info=sys.exc_info())
        raise e


def resize_tex(in_tex, out_tex, out_res=512):
    try:
        houdini_root = os.environ.get("HFS")
        hoiio_path = os.path.join(houdini_root, "bin", get_executable("hoiiotool"))

        arguments = [
            hoiio_path,
            in_tex,
            "-resize", f"{out_res}x{out_res}",
            "-o",
            out_tex
        ]

        subprocess.run(arguments, check=True)
    except Exception as e:
        set_log("Error resizing texture", exc_info=sys.exc_info())
        raise e


def set_tex_space(tex_space, tex_ext):
    try:
        if tex_space == "sRGB":
            if tex_ext == "exr":
                new_tex_space = "lin_rec709_srgb"
            else:
                new_tex_space = "srgb_tx"
        elif tex_space == "Linear":
            new_tex_space = "Utility - Raw"
        else:
            raise ValueError(f"Unknown input color space: {tex_space}")

        return new_tex_space
    except Exception as e:
        set_log("Error getting texture color space", exc_info=sys.exc_info())
        raise e


def get_new_tex_ext(hda):
    try:
            new_tex_ext = None
            convert_ext = hda.evalParm("convert_ext")
            if convert_ext == 0:
                new_tex_ext = ".rat"
            elif convert_ext == 1:
                new_tex_ext = ".exr"

            return new_tex_ext
    except Exception as e:
        set_log("Error getting texture extension", exc_info=sys.exc_info())
        raise e


def get_lod(hda):
    _lod_list = hda.evalParm("lod_list")
    lod_list = ast.literal_eval(_lod_list)
    lod_tokens = lod_list[::2]
    lod_index = hda.evalParm("lod")

    if hda.evalParm("mult_lod"):
        has_vars_parm = hda.parm("has_vars")
        if has_vars_parm:
            has_var = has_vars_parm.eval()
        else:
            has_var = 1

        if not has_var:
            iteration_count = hda.node("imp_geo_01").evalParm("inter_count")
            lod_index = hda.evalParm(f"remap_lod_{iteration_count}")
            lod = lod_tokens[lod_index]
        else:
            iteration_count = hda.node("imp_geo_01").evalParm("inter_count")
            lod_index = hda.evalParm(f"remap_lod_{iteration_count}")
            lod = lod_tokens[lod_index]

    else:
        lod = lod_tokens[lod_index]

    return lod