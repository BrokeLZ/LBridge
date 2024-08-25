import sys
from .logging_setup import set_log

tex_list: list = [
            "Albedo",
            "Specular",
            "Roughness",
            "Normal",
            "Displacement"
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

        # Has Variants
        if "scatter" in rd["tags"] or "scatter" in rd["categories"] or "cmb_asset" in rd["tags"] or "cmb_asset" in rd["categories"]:
            ad["hasVars"] = True
        else:
            ad["hasVars"] = False

        # ----- Texture Data -----
        ad["texDirs"] = rd["components"]
        ad["mapName"] = rd["mapNameOverride"]
        ad["res"] = rd["resolution"]
        ad["resVal"] = rd["resolutionValue"]
        ad["averageColor"] = rd["averageColor"]

        # ----- Meta Data -----
        ad["category"] = rd["category"]
        ad["tags"] = rd["tags"]

        asset_data = ad
        return asset_data
    except Exception as e:
        set_log("Error stripping received asset data", exc_info=sys.exc_info())
        raise e
