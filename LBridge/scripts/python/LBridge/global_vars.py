import re
import sys
import os
from .logging_setup import set_log

tex_list: list = [
            "Albedo",
            "Specular",
            "Roughness",
            "Normal",
            "Displacement"
        ]

tex_list_plant: list = [
            "Albedo",
            "Specular",
            "Roughness",
            "Normal",
            "Displacement",
            "Opacity",
            "Translucency"
        ]

asset_settings: dict = {
    "root": "",
    # LOD
    "lod": 1,
    # Proxy
    "use_prox": True,
    "prox_type": 0,
    # Shader
    "use_shader": True,
    "use_custom_shader": False,
    # Textures to use
    "use_albedo": True,
    "use_specular": True,
    "use_roughness": True,
    "use_normal": True,
    "use_displacement": True,
    # Tex Convert
    "use_rat": False,
    "convert_ext": 0,
    "convert_space": 0,
}

asset_settings_default = asset_settings


def get_tex_list():
    return tex_list

def get_tex_list_plant():
    return tex_list_plant


def set_asset_settings(settings_key, settings_value):
    try:
        global asset_settings
        asset_settings[settings_key] = settings_value
    except Exception as e:
        set_log("Failed to set asset settings global variable", exc_info=sys.exc_info())
        raise e


def get_asset_settings(settings_key="all"):
    try:
        if settings_key == "all":
            return asset_settings
        else:
            return asset_settings[settings_key]
    except Exception as e:
        set_log(f"Failed to get asset settings from global variable: {e}", exc_info=sys.exc_info())


def get_asset_settings_default(settings_key="all"):
    try:
        if settings_key == "all":
            return asset_settings_default
        else:
            return asset_settings_default[settings_key]
    except Exception as e:
        set_log(f"Failed to get asset settings defaults from global variable: {e}", exc_info=sys.exc_info())


def strip_received_data(received_data):
    try:
        rd = received_data[0]
        ad = dict()

        # ----- Main Data -----
        ad["geoDirs"] = rd["lodList"]
        ad["rootDir"] = rd["path"]
        ad["id"] = rd["id"]
        ad["name"] = rd["name"]
        ad["type"] = rd["type"]
        ad["minLOD"] = rd["minLOD"]

        # Has Variants
        if "scatter" in rd["tags"] or "scatter" in rd["categories"] or "cmb_asset" in rd["tags"] or "cmb_asset" in rd["categories"]:
            ad["hasVars"] = True
        else:
            ad["hasVars"] = False

        # ----- Texture Data -----
        ad["texDirs"] = rd["components"]
        if rd["type"] == "3dplant":
            ad["texDirs_Billboard"] = rd["components-billboard"]


        albedo_tex: list = []
        normal_tex: list = []
        asset_dir = rd["path"]
        if rd["type"] == "3dplant":
            os.path.join(asset_dir, "Textures", "Atlas")

        lod_albedo_pattern = re.compile(r".*Albedo(_LOD\d+)?.*")
        lod_normal_pattern = re.compile(r".*Normal(_LOD\d+)?.*")
        for file in os.listdir(asset_dir):
            if lod_albedo_pattern.match(file):
                albedo_tex.append(file)
            elif lod_normal_pattern.match(file):
                normal_tex.append(file)

        ad["albedo_tex"] = str(albedo_tex)
        ad["normal_tex"] = str(normal_tex)


        # ----- Meta Data -----
        ad["category"] = rd["category"]
        ad["tags"] = rd["tags"]

        asset_data = ad
        return asset_data
    except Exception as e:
        set_log("Error stripping received asset data", exc_info=sys.exc_info())
        raise e
