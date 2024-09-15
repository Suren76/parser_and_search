import json
import os
from pathlib import Path

import requests

from api.api import API
from utils.get_random_phpsessid_cookie import get_random_phpsessid_cookie


def download_image_by_id(_id: str, _path_to_save=".") -> str:
    data = json.loads(os.environ.get("LIST_OF_ACTUAL_LOGIN_DATAS"))

    _search_result = API().get_model_by_id(_id, get_random_phpsessid_cookie(data))
    _image_url = _search_result.get_url_to_image
    data = requests.get(_image_url).content
    open(Path(_path_to_save)/f"{_id}.jpg", "wb").write(data)
    return
