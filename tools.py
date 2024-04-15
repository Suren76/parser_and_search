from os import PathLike
from typing import Literal

from tqdm import tqdm

from search.archives._get_id_from_archive import _get_id_from_archive


def get_image_url(url_path: str, domain: str = "https://b7.3ddd.ru"):
    return _get_image_url_from_description_carousel(url_path, domain)


def _get_image_url_from_description(url_path: str, domain: str):
    return f"{domain}/media/cache/tuk_model_custom_filter_ang_en/{url_path}"


def _get_image_url_from_description_carousel(url_path: str, domain: str):
    return f"{domain}/media/cache/sky_model_new_big_ang_en/{url_path}"


def _is_archive_valid(_path: PathLike) -> bool:
    try:
        _id_from_archive = _get_id_from_archive(_path)
    except Exception as e:
        return False
    return True


