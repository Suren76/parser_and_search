import os
from pathlib import Path
from api.api import API
from search.search_on_web import get_slug_of_model_by_image


def __get_list_of_images(_path_to_directory: str | Path):
    _files_list = {
        name: str(_path_to_directory / name)
        for name in os.listdir(_path_to_directory)

        if
        ".json" not in name and
        ".zip" not in name and ".rar" not in name and ".7z" not in name and
        ".txt" not in name

        and "__old_" not in name
    }

    # print(_files_list)

    for path_of_file in _files_list:
        file = _path_to_directory / path_of_file

        _slug = get_slug_of_model_by_image(file)
        # print(_slug)
        # ???????????????????????????????
        if type(_slug) is str:
            continue

        _id_from_by_name_found_model = API().get_id_of_model_by_slug(_slug[0])

        # print(_id_from_by_name_found_model if file.stem == _id_from_by_name_found_model else file)

        if file.stem != _id_from_by_name_found_model:
            _new_filename = file.with_stem(_id_from_by_name_found_model + "__old_" + file.stem)
            file.rename(_new_filename)


def add_id_to_image_name(_path_to_directory: Path, path_to_cookies_file: str | Path):
    from dotenv import load_dotenv
    load_dotenv(Path(path_to_cookies_file).parent / ".env.secret")
    __get_list_of_images(_path_to_directory)
