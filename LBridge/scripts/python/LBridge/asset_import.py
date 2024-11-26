import hou
import os
import ast
import sys
from .utils import fix_escape_chars, fix_path, resize_tex
from .global_vars import get_tex_list, get_asset_settings
from .logging_setup import set_log


def import_asset(asset_data):
    try:
        if asset_data["type"] == "3d":
            imp_simple_3d_asset(asset_data)
        elif asset_data["type"] == "3dplant":
            imp_simple_3d_plant(asset_data)

        else:
            message = f"Asset type: {asset_data['type']} is not supported, please limit yourself to '3d' Assets"
            set_log(message)
            print(message)
            hou.ui.displayMessage(message, severity=hou.severityType.Error, title="Wrong Asset Type")
    except KeyError as e:
        set_log(f"KeyError in asset data: {e}", exc_info=sys.exc_info())
        raise e
    except Exception as e:
        set_log("Unexpected error in import_asset", exc_info=sys.exc_info())
        raise e


def imp_simple_3d_asset(asset_data):
    try:
        # Get Settings
        settings = get_asset_settings()
        if not settings:
            raise ValueError("Failed to get asset settings")

    except Exception as e:
        set_log("Failed to get import settings for hda", exc_info=sys.exc_info())
        raise e

    try:
        user_input_root_path = settings["root"]
        user_input_container = hou.node(user_input_root_path)
        default_root = "/obj/quixel_assets"

        if not user_input_container or not user_input_container.isNetwork() or not user_input_container.isEditable() or not user_input_container.childTypeCategory().name() == "Lop":
            root_path = default_root
            if not hou.node(root_path):
                hou.node("/obj").createNode("lopnet", node_name="quixel_assets")
        else:
            root_path = user_input_root_path

    except Exception as e:
        set_log("Failed to set or create root container for asset_import", exc_info=sys.exc_info())
        raise e

    try:
        # HDA creation
        hda = hou.node(root_path).createNode("megascan_simple_3d_asset_import")
        hda.setName(asset_data["name"].replace(" ", "_"), True)
        hda.moveToGoodPosition()
    except Exception as e:
        set_log("Failed to create HDA for asset", exc_info=sys.exc_info())
        raise e

    try:
        # Set Asset Data
        hda.parm("name").set(asset_data["name"])
        hda.parm("id").set(asset_data["id"])
        hda.parm("has_vars").set(asset_data["hasVars"])

        dirs_model = fix_escape_chars(asset_data["geoDirs"])
        hda.parm("dirs_model").set(dirs_model)
        tex_dirs = fix_escape_chars(asset_data["texDirs"])
        hda.parm("dirs_tex").set(tex_dirs)
        hda.parm("albedo_tex").set(asset_data["albedo_tex"])
        hda.parm("normal_tex").set(asset_data["normal_tex"])

        hda.parm("load_lod").pressButton()
    except KeyError as e:
        set_log(f"KeyError when settings asset parameters: {e}", exc_info=sys.exc_info())
        raise e
    except Exception as e:
        set_log("Failed to set asset data on the hda", exc_info=sys.exc_info())
        raise e

    try:
        try:
            # Set Which Textures to use
            tex_list = get_tex_list()
            for tex in tex_list:
                check_state = settings[f"use_{tex.lower()}"]
                hda.parm(f"use_{tex.lower()}").set(check_state)
                hda.parm(f"use_{tex.lower()}").pressButton()

        except KeyError as e:
            set_log(f"KeyError when setting texture parameters: {e}", exc_info=sys.exc_info())
            raise e
        except Exception as e:
            set_log("Failed to set textures to use", exc_info=sys.exc_info())
            raise e

        # Configure Settings
        hda.parm("lod").set(settings["lod"])

        hda.parm("use_proxy").set(settings["use_prox"])
        hda.parm("proxy_type").set(settings["prox_type"])

        hda.parm("use_shader").set(settings["use_shader"])
        hda.parm("use_custom_shader").set(settings["use_custom_shader"])

        hda.parm("use_rat").set(settings["use_rat"])
        hda.parm("convert_ext").set(settings["convert_ext"])
        hda.parm("convert_space").set(settings["convert_space"])
        if hda.parm("use_rat").eval():
            hda.parm("convert_tex").pressButton()

    except Exception as e:
        set_log(f"Failed to configure hda settings: {e}", exc_info=sys.exc_info())
        raise e

    try:
        # Create Preview Tex
        tex_dirs_list = ast.literal_eval(tex_dirs)
        for tex_dict in tex_dirs_list:
            if tex_dict["type"] == "albedo":
                tex_path = tex_dict["path"]
                if tex_path:
                    tex_path = fix_path(tex_path, os.path.sep)
                    split_tex_path = os.path.splitext(tex_path)
                    preview_tex_path = f"{split_tex_path[0]}_Preview{split_tex_path[1]}"

                    if not os.path.exists(preview_tex_path):
                        resize_tex(tex_path, preview_tex_path)

    except Exception as e:
        message = "Failed to create preview texture"
        set_log(f"message: {e}", exc_info=sys.exc_info())
        print(message)

    set_log(f"Successfully imported asset: {asset_data['name']}:{asset_data['id']}", "Message")


def imp_simple_3d_plant(asset_data):
    try:
        # Get Settings
        settings = get_asset_settings()
        if not settings:
            raise ValueError("Failed to get asset settings")

    except Exception as e:
        set_log("Failed to get import settings for hda", exc_info=sys.exc_info())
        raise e

    try:
        user_input_root_path = settings["root"]
        user_input_container = hou.node(user_input_root_path)
        default_root = "/obj/quixel_assets"

        if not user_input_container or not user_input_container.isNetwork() or not user_input_container.isEditable() or not user_input_container.childTypeCategory().name() == "Lop":
            root_path = default_root
            if not hou.node(root_path):
                hou.node("/obj").createNode("lopnet", node_name="quixel_assets")
        else:
            root_path = user_input_root_path

    except Exception as e:
        set_log("Failed to set or create root container for asset_import", exc_info=sys.exc_info())
        raise e

    try:
        # HDA creation
        hda = hou.node(root_path).createNode("megascan_simple_3d_plant_import")
        hda.setName(asset_data["name"].replace(" ", "_"), True)
        hda.moveToGoodPosition()
    except Exception as e:
        set_log("Failed to create HDA for asset", exc_info=sys.exc_info())
        raise e

    try:
        # Set Asset Data
        hda.parm("name").set(asset_data["name"])
        hda.parm("id").set(asset_data["id"])
        hda.parm("minLOD").set(asset_data["minLOD"])

        dirs_model = fix_escape_chars(asset_data["geoDirs"])
        hda.parm("dirs_model").set(dirs_model)
        tex_dirs = fix_escape_chars(asset_data["texDirs"])
        hda.parm("dirs_tex").set(tex_dirs)
        tex_dirs_billboard = fix_escape_chars(asset_data["texDirs_Billboard"])
        hda.parm("dirs_tex_billboard").set(tex_dirs_billboard)

        variant_count: list = []
        for dir_model in ast.literal_eval(dirs_model):
            variant = dir_model["variation"]
            if variant in variant_count:
                continue
            variant_count.append(variant)
        hda.parm("var_count").set(len(variant_count))


        hda.parm("load_lod").pressButton()
    except KeyError as e:
        set_log(f"KeyError when settings asset parameters: {e}", exc_info=sys.exc_info())
        raise e
    except Exception as e:
        set_log("Failed to set asset data on the hda", exc_info=sys.exc_info())
        raise e

    try:
        try:
            # Set Which Textures to use
            tex_list = get_tex_list()
            for tex in tex_list:
                check_state = settings[f"use_{tex.lower()}"]
                hda.parm(f"use_{tex.lower()}").set(check_state)
                hda.parm(f"use_{tex.lower()}").pressButton()

        except KeyError as e:
            set_log(f"KeyError when setting texture parameters: {e}", exc_info=sys.exc_info())
            raise e
        except Exception as e:
            set_log("Failed to set textures to use", exc_info=sys.exc_info())
            raise e

        # Configure Settings
        hda.parm("lod").set(settings["lod"])

        hda.parm("use_proxy").set(settings["use_prox"])
        hda.parm("proxy_type").set(settings["prox_type"])

        hda.parm("use_shader").set(settings["use_shader"])
        hda.parm("use_custom_shader").set(settings["use_custom_shader"])

        hda.parm("use_rat").set(settings["use_rat"])
        hda.parm("convert_ext").set(settings["convert_ext"])
        hda.parm("convert_space").set(settings["convert_space"])
        if hda.parm("use_rat").eval():
            hda.parm("convert_tex").pressButton()

    except Exception as e:
        set_log(f"Failed to configure hda settings: {e}", exc_info=sys.exc_info())
        raise e

    try:
        # Create Preview Tex
        tex_dirs_list = ast.literal_eval(tex_dirs)
        tex_dirs_billboard_list = ast.literal_eval(tex_dirs_billboard)

        for tex_dirs in [tex_dirs_list, tex_dirs_billboard_list]:
            for tex_dict in tex_dirs:
                if tex_dict["type"] == "albedo":
                    tex_path = tex_dict["path"]
                    if tex_path:
                        tex_path = fix_path(tex_path, os.path.sep)
                        split_tex_path = os.path.splitext(tex_path)
                        preview_tex_path = f"{split_tex_path[0]}_Preview{split_tex_path[1]}"

                        if not os.path.exists(preview_tex_path):
                            resize_tex(tex_path, preview_tex_path)

    except Exception as e:
        message = "Failed to create preview texture"
        set_log(f"message: {e}", exc_info=sys.exc_info())
        print(message)

    set_log(f"Asset: {asset_data['name']}:{asset_data['id']} was successfully imported", "Message")
