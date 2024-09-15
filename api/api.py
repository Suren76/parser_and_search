import base64
import os
import random
import time
from typing import Literal, Match, TypeAlias

import requests
import json

import config
from utils.get_random_bearer_token import get_random_bearer_token
from .models import ModelTagsListResponse, ModelDescriptionResponse, UserDataResponse, SearchResponse, \
    ImageSearchResponse, ModelDescriptionData


class API:

    def tags_list(self, model_slug: str) -> ModelTagsListResponse:
        url = "https://tags.3ddd.ru/api/tags/list"

        payload = json.dumps({
            "entity": "model",
            "slug": model_slug,
            "locale": "en"
        })

        response = requests.post(url, data=payload)

        return ModelTagsListResponse.model_validate(response.json())

    def model_description(self, model_slug: str) -> ModelDescriptionResponse:
        url = "https://models.3ddd.ru/api/models/show"

        payload = json.dumps({
            "slug": model_slug
        })

        data = json.loads(os.environ.get("LIST_OF_ACTUAL_LOGIN_DATAS"))

        headers = {
            "Authorization": f"{get_random_bearer_token(data)}"
        }

        response = requests.post(url, data=payload, headers=headers)

        return ModelDescriptionResponse.model_validate(response.json())

    def get_id_of_model_by_slug(self, _slug) -> str | None:
        model_description = self.model_description(_slug)
        if type(model_description.data) is ModelDescriptionData:
            return model_description.get_id
        else:
            return None

    def get_user_data(self, _user_phpsessid: str) -> UserDataResponse:
        url = "https://3dsky.org/api/user/user_data"

        headers = {
            'Cookie': f'PHPSESSID={_user_phpsessid};'
        }

        response = requests.get(url, headers=headers)
        return UserDataResponse.model_validate(response.json())

    def is_phpsessid_valid(self, _user_phpsessid: str) -> bool:
        _user_data = self.get_user_data(_user_phpsessid).data.user
        return False if _user_data is None else True if type(_user_data) is dict else "error"

    def is_bearer_token_valid(self, _bearer_token: str) -> bool:

        url = "https://models.3ddd.ru/api/models/show"

        payload = json.dumps({
            "slug": "abcd"
        })

        headers = {
            "Authorization": f"Bearer {_bearer_token}"
        }

        response = requests.post(url, data=payload, headers=headers)

        return True if response.status_code == 404 else False if response.status_code == 401 else "error"

        # return ModelDescriptionResponse.model_validate(response.json())


        # _user_data = self.get_user_data(_bearer_token).data.user
        # return False if _user_data is None else True if type(_user_data) is dict else "error"

    def get_model_by_id(self, _id, _cookie:str) -> ModelDescriptionResponse:

        _serialized_response = self.search_models(_id, _cookie)
        return self.model_description(_serialized_response.data.models[0].slug)

    def search_models(self, text_to_search: str, _cookie: str = None, _authorization: str = None, _limit: int = 100) -> SearchResponse | Literal["too big search result"] | False:
        url = "https://3dsky.org/api/models"

        payload = json.dumps({
            "query": text_to_search,
            "order": "relevance"
        })

        header = {
        }

        if _cookie:
            header["Cookie"] = _cookie
        if _authorization:
            header["Authorization"] = _authorization

        try:
            response = requests.post(url, headers=header, data=payload)
        except Exception as e:
            try:
                response = requests.post(url, headers=header, data=payload, timeout=5)
            except Exception as e:
                meta = (f"request: ({url=},{header=},{payload=})"
                        f"{text_to_search=} \n")
                print("meta for error requests", meta)
                print("sleep minute")
                time.sleep(60)
            try:
                response = requests.post(url, headers=header, data=payload, timeout=5)
            except Exception as e:
                print("request doesn't done")
                print(f"{meta=}")
                return False

        _first_deserialized_response = SearchResponse.model_validate(response.json())

        if _first_deserialized_response.data.total_value > _limit:
            return "too big search result"

        if _first_deserialized_response.data.total_value <= 60:
            return _first_deserialized_response

        # bad part
        # +2 is bad
        # do one more request
        for i in range(2, round(int(_first_deserialized_response.data.total_value)/60)+2):
            _payload = json.dumps({
                "query": text_to_search,
                "order": "relevance",
                "page": i
            })

            _response = requests.post(
                url,
                data=_payload
            )

            _response_deserialized = SearchResponse.model_validate(_response.json())

            _first_deserialized_response.data.models = _first_deserialized_response.data.models + _response_deserialized.data.models

        return _first_deserialized_response

    def search_models_by_image(self, image_base64: bytes) -> ImageSearchResponse:
        url = "https://images-search.3dsky.org/api/nearest_images"

        payload = json.dumps({
            "url": None,
            "base64_img": image_base64.decode("utf-8"),
            "es_index": "images-search",
            "n_images": 100
        })

        _response = requests.post(url, data=payload)

        return ImageSearchResponse.model_validate(_response.json())

    def search_models_by_image_and_text(self, images_search_result: ImageSearchResponse, text_to_search: str) -> SearchResponse:
        url = "https://3dsky.org/api/models"

        payload = json.dumps({
            "query": text_to_search,
            "order": "slugs",
            "model_slugs": images_search_result.slugs_list,
            "search_by_image": True
        })

        _response = requests.post(url, data=payload)

        return SearchResponse.model_validate(_response.json())

    def is_image_server_alive(self):
        url = "https://images-search.3dsky.org/api/nearest_images"

        payload = json.dumps({
            "url": None,
            "base64_img": base64.b64encode(open(config.PATH_TO_RESOURCES_DIRECTORY / "example_of_item_image.jpg", "rb").read()).decode("utf-8"),
            "es_index": "images-search",
            "n_images": 100
        })

        _response = requests.post(url, data=payload)

        return True if 0 < _response.status_code < 500 else False

    def get_bearer_token(self, _refresh_token: str) -> dict:
        url = "https://auth.3dsky.org/api/token/refresh"

        payload = json.dumps({
            "refresh_token": _refresh_token
        })

        _response = requests.post(url, data=payload)
        return _response.json()["data"]


