import json
import os
import re
from pathlib import Path

from api.api import API
from search.archives._get_id_from_archive import _get_id_from_archive
from search.search_on_web import get_slug_of_model_by_text, get_slug_of_model_by_image
from utils.utils import remove_scopes


def get_files_formatted_dict(_path_to_archives: Path, _debug: bool = False):
    _files_list = {
        name: _path_to_archives / name
        for name in os.listdir(_path_to_archives)

        if ".json" not in name
    }

    # second phase
    # second_phase = [filename for filename in _files_list if filename not in _list_of_values_to_exclude]

    filenames_list = {
        Path(file).stem.replace("_", " "): {
            "image": [],
            "archive": [],
            "unknown": [],
            "meta": [],
            "path": _path_to_archives,
            "fails": {
                "id_as_name": [],
                "id_from_archive": [],
                "from_text_if_found_one_result": [],
                "from_text_filter_by_images": [],
                "native_image_search": [],
                "native_image_search_excluded_models": []
            },
            "status": False
        }

        for file in _files_list
    }

    # print(filenames_list)

    for _item in _files_list:
        try:
            if "_" in _item:
                _old_filename = _item
                _item = _item.replace("_", " ")
                print(_item)

                _item = Path(_path_to_archives, _old_filename).rename(
                    Path(_path_to_archives, _item)
                )
                _item = str(_item)

                # filenames_list[Path(_item).stem] = filenames_list.pop(Path(_old_filename).stem)
                filenames_list[Path(_item).stem]["meta"].append(
                    {"old_filename": _old_filename}
                )

            filenames_list[Path(_item).stem][
                "archive" if ".zip" in _item or ".rar" in _item or ".7z" in _item else
                "image" if ".jpeg" in _item or ".jpg" in _item or ".png" in _item or ".webp" in _item else
                "unknown"
            ].append(_item)
        except Exception as e:
            e.add_note(_item)
            if _debug:
                print(e)
                continue
            raise e
    return filenames_list


def _get_list_of_files_with_index_as_name(_path_to_archives: Path, _debug: bool = False):
    _files_list = {
        name: _path_to_archives / name
        for name in os.listdir(_path_to_archives)
    }

    # first phase
    ids_list = [
        name
        for name in _files_list
        if Path(name).stem.count(".") == 1
        if re.match("\d+.\w+.", name) is not None
    ]
    # ids_list_filtered_singles = [_id for _id in set(ids_list) if ids_list.count(_id) == 2]

    return {filename: _files_list[filename] for filename in ids_list}


def get_list_of_archives_containing_indexes(files_dict: dict, _debug: bool = False):
    _dict = {}
    _failed_files_list = []

    for _filename_without_extension in files_dict:

        if _debug:
            print(_filename_without_extension)
        #     print(_filtered_files_list[item])

        if len(files_dict[_filename_without_extension]["archive"]) == 0:
            if _debug: print(files_dict[_filename_without_extension])
            continue

        _path_to_file = Path(files_dict[_filename_without_extension]["path"]) / files_dict[_filename_without_extension]["archive"][0]

        try:
            _id_from_archive = _get_id_from_archive(_path_to_file)
        except Exception as e:
            e.add_note(f"{_path_to_file=}")
            if _debug:
                print(e)
                continue
            _failed_files_list.append(_path_to_file)
            continue
            # raise e

        if _debug:
            print(_path_to_file)
            print(_id_from_archive)

        if _id_from_archive is None:
            continue
        elif type(_id_from_archive) is not str and type(_id_from_archive) is list:
            _id_from_archive = _id_from_archive[-1]

        if _debug:
            print(f"------------------|------|{_id_from_archive}|-----")
            print(f"------------------|------|{_filename_without_extension}|-----")
        _dict[_filename_without_extension] = _id_from_archive

        # (
        #     open(config.PATH_TO_OUTPUT_DIRECTORY / f"{str(datetime.datetime.now())}.txt", "w+")
        #     .write(get_textfile(get_slug_of_model_by_text(_id)))
        # )

    if len(_failed_files_list) > 0:
        print(f"{_failed_files_list=}")

    return _dict


def get_excluded_files_list(_path_to_archives: Path, _list_of_values_to_exclude: list, _debug: bool = False):
    _files_list = {
        name: _path_to_archives / name
        for name in os.listdir(_path_to_archives)
    }

    # second phase
    second_phase = [filename for filename in _files_list if filename not in _list_of_values_to_exclude]

    filenames_list = {
        Path(file).stem.replace("_", " "): {
            "image": [],
            "archive": [],
            "unknown": [],
            "path": _path_to_archives
        }

        for file in second_phase
    }

    for _item in second_phase:
        try:
            if "_" in _item:
                _old_filename = _item
                _item = _item.replace("_", " ")
                print(_item)
                # filenames_list[Path(_item).stem] = filenames_list.pop(Path(_old_filename).stem)
                # filenames_list[Path(_item).stem]["meta"].append(
                #     {"old_filename": _old_filename}
                # )
            filenames_list[Path(_item).stem][
                "archive" if ".zip" in _item or ".rar" in _item or ".7z" in _item else
                "image" if ".jpeg" in _item or ".jpg" in _item or ".png" in _item or ".webp" in _item else
                "unknown"
            ].append(_item)
        except Exception as e:
            if _debug:
                print(_item)
                continue
            raise e
    return filenames_list


def get_list_of_files_with_name_found_one_result(_list_of_files: dict, path_to_save: str | Path, _debug: bool = False):
    _list_of_models = {}

    for _text_to_search in _list_of_files:
        if _debug: print(_text_to_search)

        _slug = get_slug_of_model_by_text(remove_scopes(_text_to_search))

        if type(_slug) is dict:
            if _slug.get("message") == "request fails":
                if _debug: print("request fails")
                continue

        if type(_slug) is dict:
            if _slug.get("message") == "there are no found models on site":
                if _debug: print("there are no found models on site")

                continue

        if type(_slug) is dict:
            if _slug.get("message") == "too big search result":
                if _debug: print("too big search result")

                continue

        if type(_slug) is dict:
            if _slug.get("message") == "there is more than one model":

                if _debug: print("there is more than one model")
                # _list_of_models[_text_to_search] = _slug.get("models")
                continue

        _id_from_by_name_found_model = API().get_id_of_model_by_slug(_slug)

        _list_of_models[_text_to_search] = _id_from_by_name_found_model

        # print(_id_from_by_name_found_model)
        # textfile_by_id(_id_from_by_name_found_model, path_to_save)

    return _list_of_models


def get_list_of_files_with_founded_by_image_result(
        _list_of_files: dict, path_to_save: str | Path, _debug: bool = False
) -> dict[str, str | dict]:
    _file_with_error_models = open(Path("/home/suren/Projects/upwork/maroz/parser_and_search") / Path(path_to_save) / "error.json", "w+")
    __models_with_error = {}
    _list_of_models = {}

    for _text_to_search in _list_of_files:
        _file_model = _list_of_files[_text_to_search]

        if _debug: print(_text_to_search)

        if len(_file_model["image"]) == 0:
            if _debug: print(f"{_text_to_search}: there are no image with current name")
            continue
        if len(_file_model["archive"]) == 0:
            if _debug: print(f"{_text_to_search}: there are no archive with current image")
            continue

        try:
            _slug = get_slug_of_model_by_image(Path(_file_model["path"]) / _file_model["image"][0])
        except Exception as e:
            meta = f"filename: {_text_to_search}, exception: {e}"
            __models_with_error[_text_to_search] = f"get_slug phase \n" + meta

            if _debug: print(meta)
            # e.add_note(meta)
            # raise e
            continue

        if type(_slug) is dict:
            if _slug.get("message") == "there are no found models on site":
                if _debug: print("there are no found models on site")

                continue

        if type(_slug) is list:
            try:
                _list_of_models[_text_to_search] = {"to_exclude": API().get_id_of_model_by_slug(_slug[0])}
            except Exception as e:
                meta = f"filename: {_text_to_search}, slug: {_slug}, exception: {e}"
                __models_with_error[_text_to_search] = f"to_exclude phase \n" + meta

                if _debug: print(meta)
                # e.add_note(meta)
                # raise e

            continue

        try:
            _id_from_by_name_found_model = API().get_id_of_model_by_slug(_slug)
        except Exception as e:
            # __models_with_error[_text_to_search] = _file_model.copy()
            meta = f"filename: {_text_to_search}, slug: {_slug}, exception: {e}"
            __models_with_error[_text_to_search] = f"get_id phase \n" + meta

            if _debug: print(meta)
            # e.add_note(meta)
            # raise e
            continue


        _list_of_models[_text_to_search] = _id_from_by_name_found_model

    _file_with_error_models.write(json.dumps(__models_with_error))

    return _list_of_models

