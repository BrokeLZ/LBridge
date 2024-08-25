import hou
import ast
import os
import sys
from .utils import fix_path, fix_escape_chars, convert_textures_in_parallel, set_tex_space, get_new_tex_ext
from .global_vars import get_tex_list
from .logging_setup import set_log


def set_lod(hda):
    menu = []

    model_dirs = hda.evalParm("dirs_model")

    model_dirs_list = ast.literal_eval(model_dirs)

    for model_dir in model_dirs_list:
        lod = model_dir["lod"]

        menu.append(lod)
        menu.append(lod.upper())

    hda.parm("lod_list").set(str(menu))
    hda.parm("lod").pressButton()

    return menu


def set_lod_menu(hda):
    lod_list = hda.evalParm("lod_list")
    menu = ast.literal_eval(lod_list)
    return menu


def set_model_path(node):
    hda = node.parent().parent()

    model_dirs = hda.evalParm("dirs_model")
    model_dirs_list = ast.literal_eval(model_dirs)

    _lod_list = hda.evalParm("lod_list")
    lod_list = ast.literal_eval(_lod_list)

    lod_tokens = lod_list[::2]
    lod_index = hda.evalParm("lod")

    if hda.evalParm("mult_lod"):
        if not hda.evalParm("has_vars"):
            iteration_count = hda.node("imp_geo_01").evalParm("inter_count")
            lod_index = hda.evalParm(f"remap_lod_{iteration_count}")
            lod = lod_tokens[lod_index]
        else:
            iteration_count = hda.node("imp_geo_01").evalParm("inter_count")
            lod_index = hda.evalParm(f"remap_lod_{iteration_count}")
            lod = lod_tokens[lod_index]

    else:
        lod = lod_tokens[lod_index]

    geo_path = None
    for model_dict in model_dirs_list:
        if model_dict["lod"] == lod:
            geo_path = model_dict["path"]
            geo_path = fix_escape_chars(geo_path)
            geo_path = fix_path(geo_path)

    return geo_path


def set_tex_path(node):
    hda = node.parent().parent().parent()

    tex = node.name()
    tex_dirs = hda.evalParm("dirs_tex")
    tex_dirs_list = ast.literal_eval(tex_dirs)
    tex_path = ""
    for tex_dic in tex_dirs_list:
        if tex_dic["type"] == tex:
            tex_path = tex_dic["path"]
            tex_path = fix_escape_chars(tex_path)
            tex_path = fix_path(tex_path)

    if hda.evalParm("use_rat"):
        new_tex_ext = get_new_tex_ext(hda)

        tex_path = f"{os.path.splitext(tex_path)[0]}{new_tex_ext}"

    return str(tex_path)


def set_tex_path_prev(node):
    hda = node.parent().parent().parent()

    tex_dirs = hda.evalParm("dirs_tex")
    tex_dirs_list = ast.literal_eval(tex_dirs)
    tex_path = ""
    for tex_dic in tex_dirs_list:
        if tex_dic["type"] == "albedo":
            tex_path = tex_dic["path"]
            tex_path = fix_escape_chars(tex_path)
            tex_path = fix_path(tex_path)

    split_tex_path = os.path.splitext(tex_path)
    prev_tex_path = f"{split_tex_path[0]}_Preview{split_tex_path[1]}"
    return str(prev_tex_path)


def convert_hda_tex(kwargs):
    try:
        hda = kwargs["node"]
        tex_list = get_tex_list()

        tex_dirs = hda.evalParm("dirs_tex")
        if not tex_dirs:
            raise ValueError("Failed to retrieve texture data from HDA parameter dirs_tex")

        tex_dirs_list = ast.literal_eval(tex_dirs)

    except Exception as e:
        set_log(f"Failed to preparing texture data for conversion", exc_info=sys.exc_info())
        raise e

    tex_conversion_data: dict = {}
    for tex_dic in tex_dirs_list:
        if tex_dic["type"].capitalize() in tex_list:
            try:
                tex_path = tex_dic["path"]
                tex_path = fix_escape_chars(tex_path)
                tex_path = fix_path(tex_path)
                tex_ext = tex_dic["format"]
                tex_space = tex_dic["colorSpace"]
            except Exception as e:
                set_log(f"Failed to retrieve {tex_dic['type']} texture data from tex_dic: {e}", exc_info=sys.exc_info())
                raise e

            try:
                new_tex_ext = get_new_tex_ext(hda)
                old_tex_path = tex_path
                new_tex_path = f"{os.path.splitext(old_tex_path)[0]}{new_tex_ext}"
            except Exception as e:
                set_log(f"Failed to set {tex_dic['type']} texture extension", exc_info=sys.exc_info())
                raise e

            try:
                in_tex_space = set_tex_space(tex_space, tex_ext)
                out_tex_space = None
                convert_space = hda.evalParm("convert_space")
                if in_tex_space == "Utility - Raw":
                    out_tex_space = in_tex_space
                elif convert_space == 0:
                    out_tex_space = "lin_ap1"
                elif convert_space == 1:
                    out_tex_space = in_tex_space
            except Exception as e:
                set_log(f"Failed to configure {tex_dic['type']} color space", exc_info=sys.exc_info())
                raise e

            tex_conversion_data[tex_dic["type"]] = [old_tex_path, new_tex_path, in_tex_space, out_tex_space]

    try:
        convert_textures_in_parallel(tex_conversion_data)
    except Exception as e:
        set_log(f"Failed to convert textures in parallel", exc_info=sys.exc_info())
        raise e


def set_tex_connect(kwargs, output_index=0):
    tex = None
    try:
        root = kwargs["node"].node("mtl_lib/mtl_basic")
        if not root:
            raise ValueError("Could not bind root variable")

        shader = root.node("surface")
        if not shader:
            raise ValueError("Could not bind shader")

        tex_list = {
            "albedo": ["cc_albedo", "base_color"],
            "specular": ["cc_specular", "specular_color"],
            "roughness": ["cc_roughness", "specular_roughness"],
            "normal": ["normalmap", "normal"],
            "displacement": ["mtlxsubtract1", "displacement"]
        }

        _tex = kwargs["parm_name"]
        tex = _tex.replace("use_", "")

        output_node = root.node(tex_list[tex][0])
        if not output_node:
            raise ValueError("Could not bind output_node")

        input_name = tex_list[tex][1]
        if not input_name:
            raise ValueError("Could not bind input_name")

        if tex == "displacement":
            shader = root.node("mtlxdisplacement")
            if not shader:
                raise ValueError("Could not bind displacement shader")

        if kwargs["script_value0"] == "on":
            shader.setNamedInput(input_name, output_node, output_index)
        elif kwargs["script_value0"] == "off":
            shader.setNamedInput(input_name, None, 0)
    except ValueError as e:
        set_log(f"An error occurred for {tex} in set_tex_connect: {e}", exc_info=sys.exc_info())
        raise e
    except Exception as e:
        set_log(f"Failed to connect/disconnect {tex}", exc_info=sys.exc_info())
        raise e


def get_save_path(node, layer=""):
    hda = node.parent()

    out_dir = hda.evalParm("out_dir")
    out_dir = fix_path(out_dir)
    out_name = hda.evalParm("out_name")

    out_format = hda.parm("out_form").menuItems()[hda.evalParm("out_form")]
    if len(layer) > 0:
        out_file = f"{out_dir}/{out_name}/{out_name}_{layer}{out_format}"
    else:
        out_file = f"{out_dir}/{out_name}/{out_name}{out_format}"

    return out_file


def node_diver(kwargs, dive_target):
    try:
        hda_path = kwargs["node"].path()
        target_node = hou.node(f"{hda_path}{dive_target}")

        if not target_node:
            raise ValueError(f"Target node {dive_target} not found")

        hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor).setCurrentNode(target_node)
        target_node.setGenericFlag(hou.nodeFlag.Display, True)

        target_node_select = target_node.children()[0]
        hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor).setCurrentNode(target_node_select)
    except Exception as e:
        set_log(f"Failed to dive into node {dive_target}: {e}", exc_info=sys.exc_info())


def auto_remap_lods(hda):
    lods = set_lod(hda)[::2]
    hda.parm("remap_lod").set(len(lods))

    for count, lod in enumerate(lods):
        hda.parm(f"remap_lod_{count}").set(count)
