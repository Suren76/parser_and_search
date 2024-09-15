import datetime
import json
import os
from pathlib import Path, PosixPath

import config
from api.api import API
from utils.get_random_phpsessid_cookie import get_random_phpsessid_cookie
from parse_file_formats.parse_file_formats import get_textfile
from utils.check_is_all_phpsessids_valid import check_is_all_login_datas_valid
from utils.get_lists_of_files import _get_list_of_files_with_index_as_name, get_excluded_files_list, \
    get_list_of_archives_containing_indexes, get_list_of_files_with_name_found_one_result, get_files_formatted_dict, \
    get_list_of_files_with_founded_by_image_result
from utils.login_and_get_cookies_on_json import get_login_datas_from_list, get_list_of_user_data, update_login_datas_list
from utils.utils import textfile_by_id, remove_file_extension
from utils.download_image_by_id import download_image_by_id
from tqdm import tqdm
import shutil
from tools import _is_archive_valid
from dotenv import load_dotenv


def get_text_files_from_path(
        _path_to_archives: Path | str,
        _path_to_save_directory: Path | str = config.PATH_TO_OUTPUT_DIRECTORY,
        _to_download_image: bool = False,
        _to_move_archives: bool = False,
        _limit_for_result_to_use_in_image_compare: int = 300,
        _debug: bool = False,
        _request_timeout: int = None,
        _path_to_login_datas_file: Path | str = None,
        _path_to_chromedriver: str | None = None,
        _old_image_search: bool = False,
        _folder_to_exclude_files: Path | str = None
):
    path_to_archives = Path(_path_to_archives)
    path_to_save_directory = Path(_path_to_save_directory)

    if _path_to_login_datas_file is None: raise ValueError("Path to login data file didn't set!!")
    path_to_login_datas_file = Path(_path_to_login_datas_file)

    load_dotenv(path_to_login_datas_file.parent / ".env.secret")
    os.environ["PATH_TO_ENVFILE"] = str(path_to_login_datas_file.parent / ".env.secret")

    if os.environ.get("LIST_OF_ACTUAL_LOGIN_DATAS") is None:
        get_login_datas_from_list(get_list_of_user_data(path_to_login_datas_file), path_to_login_datas_file.parent,
                                  _path_to_chromedriver)


    list_with_login_datas = json.loads(os.environ["LIST_OF_ACTUAL_LOGIN_DATAS"])

    if _debug: print(list_with_login_datas)
    # -d='resources/test_data/timeout_break/found_10-'
    # -O='resources/results_from_tests/timeout_break/found_10-'
    # -I
    # -MA
    # -data='resources/data/data_to_login.json'
    # -t=3

    phpsessid_check_result = check_is_all_login_datas_valid(list_with_login_datas)

    if type(phpsessid_check_result) is list:
        update_login_datas_list(
            phpsessid_check_result,
            path_to_login_datas_file.parent,
            _path_to_chromedriver
        )


    _files_dict: dict = get_files_formatted_dict(path_to_archives, _debug)
    # print(f"{_files_dict=}")


    for item in (_pbar := tqdm(_files_dict, desc="remove_solo_images at start phase")):
        _pbar.set_description(f"{'remove_solo_images phase'} | filename: [{item}]")

        if len(_files_dict[item]["archive"]) == 0 and len(_files_dict[item]["image"]) > 0:
            # print(item)
            # os.remove(Path(_files_dict[item]["path"]) / _files_dict[item]["image"][0])

            # print(item)
            _path_to_image = Path(_files_dict[item]["path"]) / _files_dict[item]["image"][0]
            if os.path.exists(_path_to_image) and os.path.isfile(_path_to_image) and not os.path.isdir(_path_to_image):
                os.remove(_path_to_image)


    files_dict: dict = get_files_formatted_dict(path_to_archives, _debug)

    # print(f"{files_dict=}")


    # print("id phase")
    # print("id_as_name phase start")
    ids_list = _get_list_of_files_with_index_as_name(path_to_archives, _debug)
    # print(ids_list)

    # print("\n")
    for item in (_pbar := tqdm(ids_list, desc="id_as_name phase")):
        _pbar.set_description(f"{'id_as_name phase'} | filename: [{item}]")
        _to_search_key = remove_file_extension(item)
        try:
            if not _is_archive_valid(Path(files_dict[_to_search_key]["path"]) / Path(files_dict[_to_search_key]["archive"][0])):
                continue

            textfile_by_id(_to_search_key, path_to_save_directory)
            files_dict[_to_search_key]["status"] = True

            _id_from_filename = _to_search_key
            # print(_id_from_filename)

            # print(f"{_to_move_archives=}")
            # print(f"{_to_download_image=}")

            # if _to_move_archives:
            #     archive_path = (Path(files_dict[_to_search_key]["path"]) / Path(files_dict[_to_search_key]["archive"][0])
            #                    .rename(f"{_to_search_key}.{Path(files_dict[_to_search_key]['path']).suffix}"))
            #     shutil.move(archive_path, path_to_save_directory)
            if _to_move_archives:
                # print("start")
                # print(str(files_dict[_to_search_key]))
                archive_path = Path(files_dict[_to_search_key]["path"]) / Path(files_dict[_to_search_key]["archive"][0])
                # print("path")

                _new_archive_path = Path(archive_path.parent, f"{_id_from_filename}{Path(files_dict[_to_search_key]['archive'][0]).suffix}")
                # print("new path ok")
                archive_path.rename(_new_archive_path)
                # print("rename ok")
                archive_path = _new_archive_path

                if not os.path.exists(Path(path_to_save_directory / archive_path.name)):
                    shutil.move(archive_path, path_to_save_directory)
                else:
                    os.remove(archive_path)
                # print("ok")

            if _to_download_image:
                if not os.path.exists(path_to_save_directory / Path(_id_from_filename + ".jpg")):
                    download_image_by_id(_to_search_key, path_to_save_directory)
                # if len(files_dict[_to_search_key]["image"]) == 0 and _to_download_image:
                #     pass
                # else:
                #     # image_path = (Path(files_dict[_to_search_key]["path"]) / Path(files_dict[_to_search_key]["image"][0])
                #     #         .rename(f"{_to_search_key}.{Path(files_dict[_to_search_key]['path']).suffix}"))
                #     # shutil.move(image_path, path_to_save_directory)
                #     image_path = Path(files_dict[_to_search_key]["path"]) / Path(files_dict[_to_search_key]["image"][0])
                #     _new_image_path = Path(image_path.parent, f"{_id_from_filename}{Path(files_dict[_to_search_key]['image'][0]).suffix}")
                #     image_path.rename(_new_image_path)
                #     image_path = _new_image_path
                #     shutil.move(image_path, path_to_save_directory)
                #     # print("ok")
        except Exception as e:
            files_dict[_to_search_key]["fails"]["id_as_name"].append(str(e))

    files_list_excluded_id_as_name = get_excluded_files_list(path_to_archives, ids_list, _debug)
    # print(f"{'-'*15}{files_list_excluded_id_as_name=}{'-'*15}, \n {'-'*15}{len(files_list_excluded_id_as_name)=}{'-'*15}")


    # print("id phase")
    # print("id_from_archive phase start")
    list_of_archive_with_indexes = get_list_of_archives_containing_indexes(files_list_excluded_id_as_name, _debug)
    # print(list_of_archive_with_indexes)

    # print("\n")
    for item in (_pbar := tqdm(list_of_archive_with_indexes, desc="id_from_archive phase")):
        _pbar.set_description(f"{'id_from_archive phase'} | filename: [{item}]")
        try:
            if not _is_archive_valid(Path(files_dict[item]["path"]) / Path(files_dict[item]["archive"][0])):
                continue

            textfile_by_id(remove_file_extension(list_of_archive_with_indexes[item]), path_to_save_directory)
            files_dict[item]["status"] = True
            _id_from_archive = Path(list_of_archive_with_indexes[item]).stem

            if _to_move_archives:
                # print(files_dict[item])
                archive_path = Path(files_dict[item]["path"]) / Path(files_dict[item]["archive"][0])

                _new_archive_path = Path(archive_path.parent, f"{_id_from_archive}{Path(files_dict[item]['archive'][0]).suffix}")
                archive_path.rename(_new_archive_path)
                archive_path = _new_archive_path

                if not os.path.exists(Path(path_to_save_directory / archive_path.name)):
                    shutil.move(archive_path, path_to_save_directory)
                else:
                    os.remove(archive_path)

            if _to_download_image:
                if not os.path.exists(path_to_save_directory / Path(_id_from_archive + ".jpeg")):
                    download_image_by_id(_id_from_archive, path_to_save_directory)
                # if len(files_dict[item]["image"]) == 0:
                #     pass
                # else:
                #     image_path = Path(files_dict[item]["path"]) / Path(files_dict[item]["image"][0])
                #
                #     _new_image_path = Path(image_path.parent, f"{_id_from_archive}{Path(files_dict[item]['image'][0]).suffix}")
                #     image_path.rename(_new_image_path)
                #     image_path = _new_image_path
                #     shutil.move(image_path, path_to_save_directory)
                #     # print("ok")
        except Exception as e:
            # TODO: bad solution, implement something without force copy
            list_of_archive_with_indexes = list_of_archive_with_indexes.copy().pop(item)

            files_dict[item]["fails"]["id_from_archive"].append(str(e))
            files_dict[item]["fails"]["id_from_archive"].append(str(item))
            # print(item)
            # print(e)


    list_of_files_excluded_both_ids = {
        item: files_list_excluded_id_as_name[item]

        for item in files_list_excluded_id_as_name
        if item not in list_of_archive_with_indexes
    }
    # for item in list_of_files_excluded_both_ids:
    #     list_of_files_excluded_both_ids[item.replace("_", " ")] = list_of_files_excluded_both_ids.get(item)
    #     list_of_files_excluded_both_ids.pop(item)

    # print(list_of_files_excluded_both_ids)
    # print(f"{'-'*15}{list_of_files_excluded_both_ids=}{'-'*15}, \n {'-'*15}{len(list_of_files_excluded_both_ids)=}{'-'*15}")

    # print("model from text")
    # print("text if found one result")

    list_of_files_by_text_with_one_found_result = list_of_files_excluded_both_ids

    # list_of_files_by_text_with_one_found_result = get_list_of_files_with_name_found_one_result(
    #     list_of_files_excluded_both_ids, path_to_save_directory, _debug
    # )
    #
    # print("\n")
    # for item in (_pbar := tqdm(list_of_files_by_text_with_one_found_result, desc="from_text if found one result")):
    #     _pbar.set_description(f"{'from_text if found one result'} | filename: [{item}]")
    #     try:
    #         if not _is_archive_valid(Path(files_dict[item]["path"]) / Path(files_dict[item]["archive"][0])):
    #             continue
    #
    #         # print("3rd")
    #         # print(f"{list_of_files_by_text_with_one_found_result[item]=}")
    #
    #         # print(list_of_files_excluded_both_ids[item])
    #         # print(files_dict[item])
    #         # if len(files_dict[item]["image"]) == 0:
    #         #     # print("image")
    #         #     files_dict[item]["fails"]["from_text_if_found_one_result"].append("there are no image with current name")
    #         #     # _final_phase[item] = list_of_files_excluded_both_ids[item]
    #         #     continue
    #
    #         if len(files_dict[item]["archive"]) == 0:
    #             # print("archive")
    #             files_dict[item]["fails"]["from_text_if_found_one_result"].append("there are no archive with current name")
    #             # _final_phase[item] = list_of_files_excluded_both_ids[item]
    #             continue
    #
    #
    #         _id_from_text_solo_found: str = list_of_files_by_text_with_one_found_result[item]
    #
    #         textfile_by_id(_id_from_text_solo_found, path_to_save_directory)
    #         files_dict[item]["status"] = True
    #
    #         if _to_move_archives:
    #             # archive_path = (Path(files_dict[item]["path"]) / Path(files_dict[item]["archive"][0])
    #             #                .rename(f"{item}.{Path(files_dict[item]['path']).suffix}"))
    #             # shutil.move(archive_path, path_to_save_directory)
    #             archive_path = Path(files_dict[item]["path"]) / Path(files_dict[item]["archive"][0])
    #
    #             _new_archive_path = Path(archive_path.parent, f"{_id_from_text_solo_found}{Path(files_dict[item]['archive'][0]).suffix}")
    #             archive_path.rename(_new_archive_path)
    #             archive_path = _new_archive_path
    #
    #             if not os.path.exists(Path(path_to_save_directory / archive_path.name)):
    #                 shutil.move(archive_path, path_to_save_directory)
    #             else:
    #                 os.remove(archive_path)
    #
    #         if _to_download_image:
    #             if not os.path.exists(path_to_save_directory / Path(_id_from_text_solo_found + ".jpg")):
    #                 download_image_by_id(_id_from_text_solo_found, path_to_save_directory)
    #             # if len(files_dict[item]["image"]) == 0:
    #             #     pass
    #             # else:
    #             #     # image_path = (Path(files_dict[item]["path"]) / Path(files_dict[item]["image"][0])
    #             #     #               .rename(f"{item}.{Path(files_dict[item]['path']).suffix}"))
    #             #     # shutil.move(image_path, path_to_save_directory)
    #             #     image_path = Path(files_dict[item]["path"]) / Path(files_dict[item]["image"][0])
    #             #     _new_image_path = Path(image_path.parent, f"{_id_from_text_solo_found}{Path(files_dict[item]['image'][0]).suffix}")
    #             #     image_path.rename(_new_image_path)
    #             #     image_path = _new_image_path
    #             #     shutil.move(image_path, path_to_save_directory)
    #             #     # print("ok")
    #
    #     except Exception as e:
    #         files_dict[item]["fails"]["from_text_if_found_one_result"].append(str(e))
    #         files_dict[item]["fails"]["from_text_if_found_one_result"].append(str(item))
    #         # print(item)
    #         # print(e)


    list_of_files_excluded_both_ids = {
        item: files_list_excluded_id_as_name[item]

        for item in files_list_excluded_id_as_name
        if item not in list_of_archive_with_indexes
    }


    # list_of_files_excluded_both_ids_and_solo_names = {
    #     item: files_dict[item]
    #
    #     for item in files_dict
    #     if item not in list_of_files_by_text_with_one_found_result
    # }
    list_of_files_excluded_both_ids_and_solo_names = list_of_files_by_text_with_one_found_result

    list_of_files_found_by_native_image_search_result = get_list_of_files_with_founded_by_image_result(
        list_of_files_excluded_both_ids_and_solo_names, path_to_save_directory, _debug
    )

    native_image_search_status = False
    try:
        # print("try start")
        for item in (_pbar := tqdm(list_of_files_found_by_native_image_search_result, desc="native_image_search phase", leave=True)):
            _pbar.set_description(f"{'native_image_search phase'} | filename: [{item}]")
            try:
                # print("\n 3rd")
                # print(f"{list_of_files_by_text_with_one_found_result=}")
                # print(list_of_files_excluded_both_ids[item])
                # print(files_dict[item])
                # print(item)
                # if len(files_dict[item]["image"]) == 0:
                #     # print("image")
                #     files_dict[item]["fails"]["from_text_if_found_one_result"].append("there are no image with current name")
                #     # _final_phase[item] = list_of_files_excluded_both_ids[item]
                #     continue

                if len(files_dict[item]["archive"]) == 0:
                    # print("archive")
                    files_dict[item]["fails"]["native_image_search"].append("there are no archive with current name")
                    # _final_phase[item] = list_of_files_excluded_both_ids[item]
                    continue

                if len(files_dict[item]["image"]) == 0:
                    files_dict[item]["fails"]["native_image_search"].append("there are no image with current name")
                    continue

                if not _is_archive_valid(Path(files_dict[item]["path"]) / Path(files_dict[item]["archive"][0])):
                    continue

                if type(list_of_files_found_by_native_image_search_result[item]) is dict and list_of_files_found_by_native_image_search_result[item].get("to_exclude") is not None:
                    print(list_of_files_found_by_native_image_search_result[item])
                    print(item)
                    continue

                _id_from_native_image_found: str = list_of_files_found_by_native_image_search_result[item]

                # print(_id_from_native_image_found)

                textfile_by_id(_id_from_native_image_found, path_to_save_directory)
                files_dict[item]["status"] = True

                if _to_move_archives:
                    # archive_path = (Path(files_dict[item]["path"]) / Path(files_dict[item]["archive"][0])
                    #                .rename(f"{item}.{Path(files_dict[item]['path']).suffix}"))
                    # shutil.move(archive_path, path_to_save_directory)
                    archive_path = Path(files_dict[item]["path"]) / Path(files_dict[item]["archive"][0])

                    _new_archive_path = Path(archive_path.parent, f"{_id_from_native_image_found}{Path(files_dict[item]['archive'][0]).suffix}")
                    archive_path.rename(_new_archive_path)
                    archive_path = _new_archive_path

                    if not os.path.exists(Path(path_to_save_directory / archive_path.name)):
                        shutil.move(archive_path, path_to_save_directory)
                    else:
                        os.remove(archive_path)
                if _to_download_image:
                    if not os.path.exists(path_to_save_directory / Path(_id_from_native_image_found + ".jpg")):
                        download_image_by_id(_id_from_native_image_found, path_to_save_directory)
                    # if len(files_dict[item]["image"]) == 0:
                    #     pass
                    # else:
                    #     # image_path = (Path(files_dict[item]["path"]) / Path(files_dict[item]["image"][0])
                    #     #               .rename(f"{item}.{Path(files_dict[item]['path']).suffix}"))
                    #     # shutil.move(image_path, path_to_save_directory)
                    #     image_path = Path(files_dict[item]["path"]) / Path(files_dict[item]["image"][0])
                    #     _new_image_path = Path(image_path.parent, f"{_id_from_text_solo_found}{Path(files_dict[item]['image'][0]).suffix}")
                    #     image_path.rename(_new_image_path)
                    #     image_path = _new_image_path
                    #     shutil.move(image_path, path_to_save_directory)
                    #     # print("ok")
            except Exception as e:
                files_dict[item]["fails"]["native_image_search"].append(str(e))
                files_dict[item]["fails"]["native_image_search"].append(str(item))
                # print(item)
                # print(e)
        if API().is_image_server_alive():
            native_image_search_status = True
    except Exception as e:
        # if not API().is_image_server_alive():
        print("\n native image search fails, maybe image server is down")
            # native_image_search_status = False


    list_of_files_excluded_both_ids_and_solo_names_and_native_image_search_models_to_exclude = {
        item: list_of_files_found_by_native_image_search_result[item].get("to_exclude")

        for item in list_of_files_found_by_native_image_search_result
        if type(list_of_files_found_by_native_image_search_result[item]) is dict and list_of_files_found_by_native_image_search_result[item].get("to_exclude") is not None
    }

    if _folder_to_exclude_files is not None:
        folder_to_exclude_files = Path(_folder_to_exclude_files)
        for item in (_pbar := tqdm(list_of_files_excluded_both_ids_and_solo_names_and_native_image_search_models_to_exclude, desc="native_image_search_excluded_models phase")):
            _pbar.set_description(f"{'native_image_search_excluded_models phase'} | filename: [{item}]")

            if len(files_dict[item]["archive"]) == 0:
                # print("archive")
                files_dict[item]["fails"]["native_image_search_excluded_models"].append("there are no archive with current name")
                # _final_phase[item] = list_of_files_excluded_both_ids[item]
                continue

            _id_from_native_image_found: str = list_of_files_excluded_both_ids_and_solo_names_and_native_image_search_models_to_exclude[item]

            textfile_by_id(_id_from_native_image_found, folder_to_exclude_files)
            files_dict[item]["status"] = True

            _path_to_image = Path(files_dict[item]["path"]) / Path(files_dict[item]["image"][0])
            _renamed_path_to_image = Path(_path_to_image.parent, f"{_id_from_native_image_found}_{_path_to_image.stem}{Path(files_dict[item]['archive'][0]).suffix}")
            _path_to_image.rename(_renamed_path_to_image)

            if os.path.exists(Path(folder_to_exclude_files / _renamed_path_to_image.name)): continue
            shutil.move(_renamed_path_to_image, folder_to_exclude_files)

            if _to_move_archives:
                # archive_path = (Path(files_dict[item]["path"]) / Path(files_dict[item]["archive"][0])
                #                .rename(f"{item}.{Path(files_dict[item]['path']).suffix}"))
                # shutil.move(archive_path, path_to_save_directory)
                archive_path = Path(files_dict[item]["path"]) / Path(files_dict[item]["archive"][0])

                _new_archive_path = Path(archive_path.parent, f"{_id_from_native_image_found}{Path(files_dict[item]['archive'][0]).suffix}")
                archive_path.rename(_new_archive_path)
                archive_path = _new_archive_path

                if not os.path.exists(Path(folder_to_exclude_files / archive_path.name)):
                    shutil.move(archive_path, folder_to_exclude_files)
                else:
                    os.remove(archive_path)


            if _to_download_image:
                if not os.path.exists(folder_to_exclude_files / Path(_id_from_native_image_found + ".jpg")):
                    download_image_by_id(_id_from_native_image_found, folder_to_exclude_files)


    list_of_files_excluded_both_ids_and_solo_names_and_native_image_search = {
        item: list_of_files_excluded_both_ids_and_solo_names[item]

        for item in list_of_files_excluded_both_ids_and_solo_names
        if item not in list_of_files_found_by_native_image_search_result
    }

    # print("model from text")
    # print("filter by images")
    # print(list_of_files_excluded_both_ids_and_solo_names)
    _final_phase = {}
    # print("\n")
    if _old_image_search or not native_image_search_status:
        print("\n old image search starts ")
        for text_to_search in (_pbar := tqdm(list_of_files_excluded_both_ids_and_solo_names, desc="from_text filter by images phase")):
            _pbar.set_description(f"{'from_text filter by images'} | filename: [{text_to_search}]")
            # print(f"{_pbar.desc} | filename: [{text_to_search}]")

            # print(datetime.datetime.now())
            # print(text_to_search)

            _models = API().search_models(
                text_to_search,
                get_random_phpsessid_cookie(list_with_login_datas),
                _limit_for_result_to_use_in_image_compare
            )

            if len(list_of_files_excluded_both_ids[text_to_search]["image"]) == 0:
                files_dict[text_to_search]["fails"]["from_text_filter_by_images"].append("there are no image with current name")
                _final_phase[text_to_search] = list_of_files_excluded_both_ids[text_to_search]
                continue

            if len(list_of_files_excluded_both_ids[text_to_search]["archive"]) == 0:
                files_dict[text_to_search]["fails"]["from_text_filter_by_images"].append("there are no archive with current name")
                _final_phase[text_to_search] = list_of_files_excluded_both_ids[text_to_search]
                continue

            if _models == "too big search result":
                files_dict[text_to_search]["fails"]["from_text_filter_by_images"].append(str(_models))
                _final_phase[text_to_search] = str(Path(list_of_files_excluded_both_ids[text_to_search]["path"]) / list_of_files_excluded_both_ids[text_to_search]["image"][0])
                continue

            if _models == "there is more than one model":
                # print(_id_filename)
                # _list_of_models[_text_to_search] = _slug.get("models")
                continue

            # print(f"{len(_models.data.models)=}")
            # print(f"{_models=}")
            _models = _models.data
            # if len(_models.models) == 0:
            #     continue

            # print(text_to_search)
            # print(list_of_files_excluded_both_ids[text_to_search]["path"])

            # print(list_of_files_excluded_both_ids[text_to_search]["image"][0])

            try:
                if not _is_archive_valid(Path(files_dict[text_to_search]["path"]) / Path(files_dict[text_to_search]["archive"][0])):
                    continue
                # print(_models)
                # print(len(_models.models))
                # print(list_of_files_excluded_both_ids[text_to_search])
                filtered_models = _models.get_model_by_image(
                    Path(list_of_files_excluded_both_ids[text_to_search]["path"]) / list_of_files_excluded_both_ids[text_to_search]["image"][0],
                    _request_timeout=_request_timeout,
                    _debug=_debug
                )
                # print(f"{filtered_models=}")

                _id_from_text_found_filtered_by_image = filtered_models[0].get_id()
                # print(f"{_id_from_text_found_filtered_by_image=}")


                if _to_move_archives:
                    # archive_path = (Path(files_dict[text_to_search]["path"]) / Path(files_dict[text_to_search]["archive"][0])
                    #                .rename(f"{text_to_search}.{Path(files_dict[text_to_search]['path']).suffix}"))
                    # shutil.move(archive_path, path_to_save_directory)
                    archive_path = Path(files_dict[text_to_search]["path"]) / Path(files_dict[text_to_search]["archive"][0])

                    _new_archive_path = Path(
                        archive_path.parent,
                        f"{_id_from_text_found_filtered_by_image}{Path(files_dict[text_to_search]['archive'][0]).suffix}"
                    )

                    archive_path.rename(_new_archive_path)
                    archive_path = _new_archive_path
                    shutil.move(archive_path, path_to_save_directory)

                if _to_download_image:
                    download_image_by_id(_id_from_text_found_filtered_by_image, path_to_save_directory)
                    # if len(list_of_files_excluded_both_ids[text_to_search]["image"]) == 0:
                    #     pass
                    # else:
                    #     # image_path = (Path(files_dict[text_to_search]["path"]) / Path(files_dict[text_to_search]["image"][0])
                    #     #               .rename(f"{text_to_search}.{Path(files_dict[text_to_search]['path']).suffix}"))
                    #     # shutil.move(image_path, path_to_save_directory)
                    #     image_path = Path(files_dict[text_to_search]["path"]) / Path(files_dict[text_to_search]["image"][0])
                    #     _new_image_path = Path(image_path.parent, f"{_id_from_text_found_filtered_by_image}{Path(files_dict[text_to_search]['image'][0]).suffix}")
                    #     image_path.rename(_new_image_path)
                    #     image_path = _new_image_path
                    #     shutil.move(image_path, path_to_save_directory)
                    #     # print("ok")

            except Exception as e:
                # print(e)
                files_dict[text_to_search]["fails"]["from_text_filter_by_images"].append(str(e))
                _final_phase[text_to_search] = Path(list_of_files_excluded_both_ids[text_to_search]["path"]) / list_of_files_excluded_both_ids[text_to_search]["image"][0]
                continue
                # raise e

            # print(filtered_models)

            if len(filtered_models) == 1:
                data = get_textfile(filtered_models[0].slug)
                _id = API().get_id_of_model_by_slug(filtered_models[0].slug)

                (
                    open(path_to_save_directory / f"{_id}.txt", "w+")
                    .write(data)
                )
                files_dict[text_to_search]["status"] = True
            else:
                files_dict[text_to_search]["fails"]["from_text_filter_by_images"].append("there are no case which matches with this file")
                _final_phase[text_to_search] = Path(list_of_files_excluded_both_ids[text_to_search]["path"]) / list_of_files_excluded_both_ids[text_to_search]["image"][0]


    # print(f"------------------------ {_final_phase=} ---------------------------")
    # print(len(_final_phase))

    files_dict_with_solo_images: dict = get_files_formatted_dict(path_to_archives, _debug)

    # print(files_dict)
    for item in (_pbar := tqdm(files_dict_with_solo_images, desc="remove_solo_images at end phase")):
        _pbar.set_description(f"{'remove_solo_images phase'} | filename: [{item}]")

        if len(files_dict_with_solo_images[item]["archive"]) == 0 and len(files_dict_with_solo_images[item]["image"]) > 0:
            # print(item)
            _path_to_image = Path(files_dict_with_solo_images[item]["path"]) / files_dict_with_solo_images[item]["image"][0]
            if os.path.exists(_path_to_image):
                # print(_path_to_image)
                os.remove(_path_to_image)

    files_dict_with_str_path = {
        item: {
            field: str(files_dict[item][field])
            if type(files_dict[item][field]) is PosixPath
            else files_dict[item][field]
            for field in files_dict[item]
        }
        for item in files_dict
    }


    # print(files_dict_with_str_path)

    data_to_save = json.dumps(files_dict_with_str_path)

    # print(data_to_save)


    with open(path_to_save_directory / f"to_generate_statistic_{str(str(datetime.datetime.now()).split('.')[:-1][0])}.json", "w+") as statistic_file:
        statistic_file.write(
            data_to_save
        )

    # print(json.loads({item: files_dict[item] for item in files_dict if not files_dict[item]["status"]}))

