from pathlib import Path

import requests

from api.api import API
from tools import get_image_url


def download_image_by_id(_id: str, _path_to_save=".") -> str:
    _search_result = API().get_model_by_id(_id)
    _image_url = _search_result.get_url_to_image
    data = requests.get(_image_url).content
    open(Path(_path_to_save)/f"{_id}.jpg", "wb").write(data)
    return
