import json
import os
from pathlib import Path

from api.api import API
from parse_file_formats.get_random_phpsessid_cookie import get_random_phpsessid_cookie
from search.images_compare import compare_images, ImageToCompare
from tools import get_image_url


def get_slug_of_model_by_text(_text: str) -> str | dict:
    list_with_phpsessids = json.loads(os.environ["LIST_OF_ACTUAL_PHPSESSID"])

    _res = API().search_models(_text, get_random_phpsessid_cookie(list_with_phpsessids))

    if _res == "too big search result":
        return {
            "message": "too big search result",
            "metadata": {
                "text": _text
            }
        }

    if len(_res.data.models) == 0:
        return {
            "message": "there are no found models on site",
            "models": _res.data
        }

    if len(_res.data.models) == 1:
        return _res.data.models[0].slug
    else:
        # print("there is more than one model")
        return {
            "message": "there is more than one model",
            "models": _res.data
        }


def get_slug_of_model_by_image(_path_to_image: Path) -> str | dict:
    import base64

    data: bytes = base64.b64encode(open(_path_to_image, "rb").read())

    _res = API().search_models_by_image(data)
    _first_result = _res.search_result[0]

    if _first_result.similarity_score*100 < 95:
        if compare_images(
                ImageToCompare(image_source_type="local", src=_path_to_image),
                ImageToCompare("web", get_image_url(_first_result.url)),

                _debug=False, _timeout=3
        ):
            return _first_result.slug

        return {
            "message": "there are no found models on site",
            "models": _res
        }

    return _first_result.slug

