import config
from .textfile_format import parse_response_to_textfile
from api.api import API
from .json_format import get_item_from_response
from search.search_on_web import get_slug_of_model_by_text


def get_json_file(_slug: str) -> str:
    _res = API().model_description(_slug)
    _res_tags = API().tags_list(_slug)

    item = get_item_from_response(_res, _res_tags)
    return item.model_dump_json()


def get_textfile(_slug: str) -> str:
    _res = API().model_description(_slug)
    _res_tags = API().tags_list(_slug)

    return parse_response_to_textfile(_res, _res_tags)


if __name__ == "__main__":
    (
        open(config.PATH_TO_OUTPUT_DIRECTORY / "file41.txt", "w+")
        .write(get_textfile(get_slug_of_model_by_text("350207.55ed1f2ad2b97")))
    )
