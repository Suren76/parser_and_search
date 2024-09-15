import datetime
import json
import os
from pathlib import Path, PosixPath

from utils.get_lists_of_files import get_files_formatted_dict


def __get_files_formatted_dict(_path_to_archives: Path, _debug: bool = False):
    _files_list = {
        name: _path_to_archives / name
        for name in os.listdir(_path_to_archives)

        if ".json" not in name
    }

    # second phase
    # second_phase = [filename for filename in _files_list if filename not in _list_of_values_to_exclude]

    filenames_list = {
        Path(file).stem: {
            "image": [],
            "archive": [],
            "txt": [],
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
                "image" if ".jpeg" in _item or ".jpg" in _item or ".png" in _item else
                "txt" if ".txt" in _item else
                "unknown"
            ].append(_item)
        except Exception as e:
            e.add_note(_item)
            if _debug:
                print(e)
                continue
            raise e
    return filenames_list


def get_statistic(_path_to_directory: Path):
    files = __get_files_formatted_dict(_path_to_directory)

    for filename in files:
        if (
                len(files[filename]["archive"]) >= 1 and
                len(files[filename]["image"]) >= 1 and
                len(files[filename]["txt"]) >= 1
        ):
            files[filename]["status"] = True

    files_dict_with_str_path = {
        item: {
            field: str(files[item][field])
            if type(files[item][field]) is PosixPath
            else files[item][field]
            for field in files[item]
        }
        for item in files
    }

    # print(files_dict_with_str_path)

    data_to_save = json.dumps(files_dict_with_str_path)

    # print(data_to_save)

    with open(_path_to_directory / f"to_generate_statistic_{str(str(datetime.datetime.now()).split('.')[:-1][0])}.json", "w+") as statistic_file:
        statistic_file.write(
            data_to_save
        )



