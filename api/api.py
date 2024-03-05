from typing import Literal

import requests
import json
from .models import SearchResponse, ModelDescriptionResponse, ModelTagsListResponse


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

    def search_models(self, text_to_search: str) -> SearchResponse | Literal["too big search result"]:
        url = "https://3dsky.org/api/models"

        payload = json.dumps({
            "query": text_to_search,
            "order": "relevance"
        })

        response = requests.post(url, data=payload)

        _first_deserialized_response = SearchResponse.model_validate(response.json())

        if _first_deserialized_response.data.total_value > 300:
            return "too big search result"

        if _first_deserialized_response.data.total_value <= 60:
            return _first_deserialized_response

        for i in range(2, round(int(_first_deserialized_response.data.total_value)/60)+1):
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
