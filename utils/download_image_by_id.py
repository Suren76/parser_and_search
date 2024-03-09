import requests

from api.api import API
from tools import get_image_url


def download_image_by_id(_id: str, _path_to_save) -> str:
    _search_result = API().search_models(_id)
    _image_url = get_image_url(_search_result.data.models[0].get_images()[0], _search_result.data.backends[0])
    data = requests.get(_image_url).content
    open(f"{_path_to_save}/{_id}.jpg", "wb").write(data)
    return
