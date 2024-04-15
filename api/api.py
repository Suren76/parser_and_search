from typing import Literal, Match, TypeAlias

import requests
import json
from .models import ModelTagsListResponse, ModelDescriptionResponse, UserDataResponse, SearchResponse, ImageSearchResponse



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

        response = requests.post(url, data=payload)

        return ModelDescriptionResponse.model_validate(response.json())

    def get_id_of_model_by_slug(self, _slug) -> str:
        return self.model_description(_slug).get_id

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

    def get_model_by_id(self, _id) -> ModelDescriptionResponse:
        response = requests.post(
            url="https://3dsky.org/api/models",
            data=json.dumps({
                "query": _id,
                "order": "relevance"
            })
        )

        _serialized_response = SearchResponse.model_validate(response.json())
        return self.model_description(_serialized_response.data.models[0].slug)

    def search_models(self, text_to_search: str, _cookie: str, _limit: int = 100) -> SearchResponse | Literal["too big search result"]:
        url = "https://3dsky.org/api/models"

        payload = json.dumps({
            "query": text_to_search,
            "order": "relevance"
        })

        header = {
            "Cookie": _cookie
        }

        response = requests.post(url, headers=header, data=payload)

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

