import os
from pathlib import Path

from api.api import API
from search.archives._get_id_from_archive import _get_id_from_archive
from search.search_on_web import get_slug_of_model_by_text
from utils.utils import textfile_by_id


def get_files_formatted_dict(_path_to_archives: Path):
    _files_list = {
        name: _path_to_archives / name
        for name in os.listdir(_path_to_archives)
    }

    # second phase
    # second_phase = [filename for filename in _files_list if filename not in _list_of_values_to_exclude]

    filenames_list = {
        Path(file).stem: {
            "image": [],
            "archive": [],
            "unknown": [],
            "path": _path_to_archives,
            "fails": {
                "id_as_name": [],
                "id_from_archive": [],
                "from_text_if_found_one_result": [],
                "from_text_filter_by_images": []
            },
            "status": False
        }

        for file in _files_list
    }

    for _item in _files_list:
        filenames_list[Path(_item).stem][
            "archive" if ".zip" in _item or ".rar" in _item or ".7z" in _item else
            "image" if ".jpeg" in _item or ".jpg" in _item or ".png" in _item else
            "unknown"
        ].append(_item)

    return filenames_list


def _get_list_of_files_with_index_as_name(_path_to_archives: Path):
    _files_list = {
        name: _path_to_archives / name
        for name in os.listdir(_path_to_archives)
    }

    # first phase
    ids_list = [name for name in _files_list if Path(name).stem.count(".") == 1]
    # ids_list_filtered_singles = [_id for _id in set(ids_list) if ids_list.count(_id) == 2]

    return {filename: _files_list[filename] for filename in ids_list}


def get_list_of_archives_containing_indexes(files_dict: dict):
    _dict = {}

    for _filename_without_extension in files_dict:
        # print(item)
        # print(_filtered_files_list[item])

        if len(files_dict[_filename_without_extension]["archive"]) == 0:
            continue

        _path_to_file = Path(files_dict[_filename_without_extension]["path"]) / files_dict[_filename_without_extension]["archive"][0]
        # print(_path_to_file)
        # print(_get_id_from_archive(_path_to_file))

        _id_from_archive = _get_id_from_archive(_path_to_file)

        if _id_from_archive is None:
            continue
        elif type(_id_from_archive) is not str:
            _id_from_archive = _id_from_archive[0]

        # print(f"------------------|------|{_id_from_archive}|-----")
        # print(f"------------------|------|{_filename_without_extension}|-----")
        _dict[_filename_without_extension] = _id_from_archive

        # (
        #     open(config.PATH_TO_OUTPUT_DIRECTORY / f"{str(datetime.datetime.now())}.txt", "w+")
        #     .write(get_textfile(get_slug_of_model_by_text(_id)))
        # )
    return _dict


def get_excluded_files_list(_path_to_archives: Path, _list_of_values_to_exclude: list):
    _files_list = {
        name: _path_to_archives / name
        for name in os.listdir(_path_to_archives)
    }

    # second phase
    second_phase = [filename for filename in _files_list if filename not in _list_of_values_to_exclude]

    filenames_list = {
        Path(file).stem: {
            "image": [],
            "archive": [],
            "unknown": [],
            "path": _path_to_archives
        }

        for file in second_phase
    }

    for _item in second_phase:
        filenames_list[Path(_item).stem][
            "archive" if ".zip" in _item or ".rar" in _item or ".7z" in _item else
            "image" if ".jpeg" in _item or ".jpg" in _item or ".png" in _item else
            "unknown"
        ].append(_item)

    return filenames_list


def get_list_of_files_with_name_found_one_result(_list_of_files: dict, path_to_save: str | Path):
    _list_of_models = {}

    for _text_to_search in _list_of_files:
        # print(_text_to_search)
        _slug = get_slug_of_model_by_text(_text_to_search)

        if type(_slug) is dict:
            if _slug.get("message") == "too big search result":
                continue

        if type(_slug) is dict:
            if _slug.get("message") == "there is more than one model":
                # print(_id_filename)
                # _list_of_models[_text_to_search] = _slug.get("models")
                continue

        _id_from_by_name_found_model = API().get_id_of_model_by_slug(_slug)

        _list_of_models[_text_to_search] = _id_from_by_name_found_model

        # print(_id_from_by_name_found_model)
        textfile_by_id(_id_from_by_name_found_model, path_to_save)

    return _list_of_models


