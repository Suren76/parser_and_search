import os
from pathlib import Path

import config
from parse_file_formats.parse_file_formats import get_textfile
from search.archives._get_id_from_archive import _get_id_from_archive
from search.search_on_web import get_slug_of_model_by_text


def textfile_by_id(_id: str, path_to_save: Path = config.PATH_TO_OUTPUT_DIRECTORY) -> object:
    _text = _id
    # print(f"--------------- {_text=} ---------------")
    data = get_textfile(get_slug_of_model_by_text(_text))
    # _id = API().get_id_of_model_by_slug(get_slug_of_model_by_text(_text))
    (
        open(path_to_save / f"{_text}.txt", "w+")
        .write(data)
    )

# def _textfile_by_text(_text: str):
#     print(_text)
#     _slug = get_slug_of_model_by_text(_text)
#
#     if type(_slug) is dict:
#         if _slug.get("message") == "too big search result":
#             continue
#
#     if type(_slug) is dict:
#         if _slug.get("message") == "there is more than one model":
#             # print(_id_filename)
#             _fourth_phase__list_of_models[text_to_search] = _slug.get("models")
#             continue
#
#     _id = API().get_id_of_model_by_slug(_slug)
#     print(_id)
#     textfile_by_id(_id)


def remove_file_extension(filename: str):
    return Path(filename).stem


def remove_scopes(text: str):
    start_index = text.find("(")
    end_index = text.find(")")+1
    return text.replace(text[start_index:end_index], "")



