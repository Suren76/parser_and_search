from api.api import API


def get_slug_of_model_by_text(_text: str) -> str | dict:
    _res = API().search_models(_text)

    if _res == "too big search result":
        return {
            "message": "too big search result",
            "metadata": {
                "text": _text
            }
        }

    if len(_res.data.models) == 1:
        return _res.data.models[0].slug
    else:
        # print("there is more than one model")
        return {
            "message": "there is more than one model",
            "models": _res.data
        }

