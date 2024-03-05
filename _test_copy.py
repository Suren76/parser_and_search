import datetime
import os
import zipfile
from pathlib import Path

import py7zr
from py7zr import Bad7zFile
from rarfile import NotRarFile

import config
from api.api import API
from api.models import SearchModelData
from search.archives._get_id_from_archive import _get_id_from_archive
from parse_file_formats.parse_file_formats import get_textfile
from search.search_on_web import get_slug_of_model_by_text


def _get_list_of_files_with_name_index(_path_to_archives: Path):
    _files_list = {
        name: _path_to_archives / name
        for name in os.listdir(_path_to_archives)
    }

    # first phase
    ids_list = [name for name in _files_list if Path(name).stem.count(".") == 1]
    # ids_list_filtered_singles = [_id for _id in set(ids_list) if ids_list.count(_id) == 2]

    return {filename: _files_list[filename] for filename in ids_list}


def get_excluded_files_list(_path_to_archives, _list_of_values_to_exclude):
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
            "archive" if "zip" in _item or "rar" in _item or "7z" in _item else
            "image" if "jpeg" in _item or "jpg" in _item or "png" in _item else
            "unknown"
        ].append(_item)

    return filenames_list


path_to_archives = Path("resources/test_data/Suren")


# files_list = {**{name: path_to_archives+"/"+name for name in os.listdir(path_to_archives)} ,**{name: path_to_archives[:-2] for name in os.listdir(path_to_archives[:-2])}}

# ids_list = [name for name in files_list if name.count(".") == 2]

# ids_list_filtered_singles = [_id for _id in set(ids_list) if ids_list.count(_id) == 2]

# second_phase = [filename for filename in files_list if filename not in ids_list]

# filenames_list =
# for file in second_phase:


# filenames_list = {file: file.split(".")[0] for file in second_phase}

# fnames_list = [
#     filename_without_extension
#
#     for filename_without_extension in set(filenames_list.values())
#
#     if list(filenames_list.values()).count(filename_without_extension) == 2
# ]

# fnames_list = {item: [] for item in set(filenames_list.values())}

# for item in set(filenames_list.values()):

    # fnames_list[item].append(filenames_list.fromkeys(item))

# print(len(second_phase))
# print(len(filenames_list))
# print(filenames_list)
# print(len(fnames_list))
# print(fnames_list)

# archives_ids_list = [_get_id_from_archive() for filename_ in fnames_list]

ids_list = _get_list_of_files_with_name_index(path_to_archives)
print(ids_list)


def textfile_by_id(_id: str):
    _text = ".".join(item.split(".")[:-1])
    print(f"--------------- {_text=} ---------------")
    data = get_textfile(get_slug_of_model_by_text(_text))
    # _id = API().get_id_of_model_by_slug(get_slug_of_model_by_text(_text))
    (
        open(config.PATH_TO_OUTPUT_DIRECTORY / f"{_text}.txt", "w+")
        .write(data)
    )


def remove_file_extension(filename: str):
    return Path(filename).stem


for item in ids_list:
    textfile_by_id(remove_file_extension(item))


print("third phase")
_third_phase__list_of_files_with_indexes = []
_third_phase__list_of_files = []
_filtered_files_list = get_excluded_files_list(path_to_archives, ids_list)

print(_filtered_files_list)
print(len(_filtered_files_list))

def get_list_of_archives_containing_indexes(files_list: dict):
    for item in _filtered_files_list:
        # print(item)
        # print(_filtered_files_list[item])
        # print(_filtered_files_list[item]["image"])
        # print(_filtered_files_list[item]["archive"])
        if len(_filtered_files_list[item]["archive"]) == 0:
            continue
        _path_to_file = _filtered_files_list[item]["path"] + "/" + _filtered_files_list[item]["archive"][0]
        # print(_path_to_file)
        # print(_get_id_from_archive(_path_to_file))

        _id = _get_id_from_archive(_path_to_file)

        if _id is None:
            continue

        _id = _id if type(_id) is str else _id[0]
        print("------------------|------|id|-----", _id)
        print("------------------|------|item|-----", item)
        _third_phase__list_of_files_with_indexes.append(item)

        # (
        #     open(config.PATH_TO_OUTPUT_DIRECTORY / f"{str(datetime.datetime.now())}.txt", "w+")
        #     .write(get_textfile(get_slug_of_model_by_text(_id)))
        # )


_third_phase__list_of_files = {
    item: _filtered_files_list[item]
    for item in _filtered_files_list
    if item not in _third_phase__list_of_files_with_indexes
}
print(_third_phase__list_of_files)
print(len(_third_phase__list_of_files))

print("fourth phase")
_fourth_phase__list_of_models = {}
for text_to_search in _third_phase__list_of_files:
    print(text_to_search)
    _slug = get_slug_of_model_by_text(text_to_search)

    if type(_slug) is dict:
        if _slug.get("message") == "too big search result":
            continue

    if type(_slug) is dict:
        if _slug.get("message") == "there is more than one model":
            # print(_id_filename)
            _fourth_phase__list_of_models[text_to_search] = _slug.get("models")
            continue

    _id = API().get_id_of_model_by_slug(_slug)

    (
        open(config.PATH_TO_OUTPUT_DIRECTORY / f"{text_to_search}.txt", "w+")
        .write(get_textfile(get_slug_of_model_by_text(text_to_search)))
    )


print("final phase")
# print(_fourth_phase__list_of_models)
_final_phase = {}
for text_to_search in _fourth_phase__list_of_models:
    print(datetime.datetime.now())
    _models: SearchModelData = _fourth_phase__list_of_models[text_to_search]
    print(text_to_search)
    print(_third_phase__list_of_files[text_to_search]["path"])

    if len(_third_phase__list_of_files[text_to_search]["image"]) == 0:
        _final_phase[text_to_search] = _third_phase__list_of_files[text_to_search]
        continue


    print(_third_phase__list_of_files[text_to_search]["image"][0])

    try:
        filtered_models = _models.get_model_by_image(_third_phase__list_of_files[text_to_search]["path"]+"/"+_third_phase__list_of_files[text_to_search]["image"][0])
    except Exception as e:
        print(e)
        raise e

    print(filtered_models)

    if len(filtered_models) == 1:
        data = get_textfile(filtered_models[0].slug)
        _id = API().get_id_of_model_by_slug(filtered_models[0].slug)

        (
            open(config.PATH_TO_OUTPUT_DIRECTORY / f"{text_to_search}.txt", "w+")
            .write(data)
        )
    else:
        _final_phase[text_to_search] = _third_phase__list_of_files[text_to_search]["path"] + "/" + _third_phase__list_of_files[text_to_search]["image"][0]
    # print(ids_list)
    # for item in ids_list:
    #     _text = ".".join(item.split(".")[:-1])
    #     print(_text)
    #     data = get_textfile(get_slug_of_model_by_text(_text))
    #     (
    #         open(config.PATH_TO_OUTPUT_DIRECTORY / f"{_text}.txt", "w+")
    #         .write(data)
    #     )

