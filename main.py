import datetime
import json
from pathlib import Path, PosixPath

import config
from api.api import API
from api.models import SearchModelData
from parse_file_formats.parse_file_formats import get_textfile
from utils.get_lists_of_files import _get_list_of_files_with_index_as_name, get_excluded_files_list, \
    get_list_of_archives_containing_indexes, get_list_of_files_with_name_found_one_result, get_files_formatted_dict
from utils.utils import textfile_by_id, remove_file_extension
from utils.download_image_by_id import download_image_by_id
from tqdm import tqdm
import shutil


def get_text_files_from_path(
        _path_to_archives: Path | str,
        _path_to_save_directory: Path | str = config.PATH_TO_OUTPUT_DIRECTORY,
        _to_download_image: bool = False,
        _to_move_archives : bool = False
):
    path_to_archives = Path(_path_to_archives)
    path_to_save_directory = Path(_path_to_save_directory)

    files_dict: dict = get_files_formatted_dict(path_to_archives)
    # print(files_dict)


    # print("id phase")
    # print("id_as_name phase start")
    ids_list = _get_list_of_files_with_index_as_name(path_to_archives)
    # print(ids_list)

    for item in tqdm(ids_list, desc="id_as_name phase"):
        _to_search_key = remove_file_extension(item)
        try:
            textfile_by_id(_to_search_key, path_to_save_directory)
            files_dict[_to_search_key]["status"] = True

            if _to_move_archives:
                archive_path = (Path(files_dict[_to_search_key]["path"]) / Path(files_dict[_to_search_key]["archive"][0])
                               .rename(f"{_to_search_key}.{Path(files_dict[_to_search_key]['path']).suffix}"))
                shutil.move(archive_path, path_to_save_directory)

            if len(files_dict[_to_search_key]["image"]) == 0 and _to_download_image:
                download_image_by_id(_to_search_key, path_to_save_directory)
            else:
                image_path = (Path(files_dict[_to_search_key]["path"]) / Path(files_dict[_to_search_key]["image"][0])
                        .rename(f"{_to_search_key}.{Path(files_dict[_to_search_key]['path']).suffix}"))
                shutil.move(image_path, path_to_save_directory)
        except Exception as e:
            files_dict[_to_search_key]["fails"]["id_as_name"].append(str(e))

    files_list_excluded_id_as_name = get_excluded_files_list(path_to_archives, ids_list)
    # print(f"{'-'*15}{files_list_excluded_id_as_name=}{'-'*15}, \n {'-'*15}{len(files_list_excluded_id_as_name)=}{'-'*15}")


    # print("id phase")
    # print("id_from_archive phase start")
    list_of_archive_with_indexes = get_list_of_archives_containing_indexes(files_list_excluded_id_as_name)
    # print(list_of_archive_with_indexes)

    for item in tqdm(list_of_archive_with_indexes, desc="id_from_archive phase"):
        try:
            textfile_by_id(remove_file_extension(list_of_archive_with_indexes[item]), path_to_save_directory)
            files_dict[item]["status"] = True

            if _to_move_archives:
                archive_path = (Path(files_dict[item]["path"]) / Path(files_dict[item]["archive"][0])
                               .rename(f"{item}.{Path(files_dict[item]['path']).suffix}"))
                shutil.move(archive_path, path_to_save_directory)

            if len(files_dict[item]["image"]) == 0 and _to_download_image:
                download_image_by_id(list_of_archive_with_indexes[item], path_to_save_directory)
            else:
                image_path = (Path(files_dict[item]["path"]) / Path(files_dict[item]["image"][0])
                              .rename(f"{item}.{Path(files_dict[item]['path']).suffix}"))
                shutil.move(image_path, path_to_save_directory)
        except Exception as e:
            files_dict[item]["fails"]["id_from_archive"].append(str(e))
            files_dict[item]["fails"]["id_from_archive"].append(str(item))
            # print(item)
            # print(e)


    list_of_files_excluded_both_ids = {
        item: files_list_excluded_id_as_name[item]

        for item in files_list_excluded_id_as_name
        if item not in list_of_archive_with_indexes
    }
    # print(f"{'-'*15}{list_of_files_excluded_both_ids=}{'-'*15}, \n {'-'*15}{len(list_of_files_excluded_both_ids)=}{'-'*15}")

    # print("model from text")
    # print("text if found one result")
    list_of_files_by_text_with_one_found_result = get_list_of_files_with_name_found_one_result(list_of_files_excluded_both_ids, path_to_save_directory)

    for item in tqdm(list_of_files_by_text_with_one_found_result, desc="from_text if found one result"):
        try:
            textfile_by_id(list_of_files_by_text_with_one_found_result[item], path_to_save_directory)
            files_dict[item]["status"] = True

            if _to_move_archives:
                archive_path = (Path(files_dict[item]["path"]) / Path(files_dict[item]["archive"][0])
                               .rename(f"{item}.{Path(files_dict[item]['path']).suffix}"))
                shutil.move(archive_path, path_to_save_directory)

            if len(files_dict[item]["image"]) == 0 and _to_download_image:
                download_image_by_id(list_of_files_by_text_with_one_found_result[item], path_to_save_directory)
            else:
                image_path = (Path(files_dict[item]["path"]) / Path(files_dict[item]["image"][0])
                              .rename(f"{item}.{Path(files_dict[item]['path']).suffix}"))
                shutil.move(image_path, path_to_save_directory)

        except Exception as e:
            files_dict[item]["fails"]["from_text_if_found_one_result"].append(str(e))
            files_dict[item]["fails"]["from_text_if_found_one_result"].append(str(item))
            # print(item)
            # print(e)


    list_of_files_excluded_both_ids_and_solo_names = {
        item: list_of_files_excluded_both_ids[item]

        for item in list_of_files_excluded_both_ids
        if item not in list_of_files_by_text_with_one_found_result
    }


    # print("model from text")
    # print("filter by images")
    # print(list_of_files_excluded_both_ids_and_solo_names)
    _final_phase = {}
    for text_to_search in tqdm(list_of_files_excluded_both_ids_and_solo_names, desc="from_text filter by images"):
        # print(datetime.datetime.now())
        # print(text_to_search)
        _models: SearchModelData = API().search_models(text_to_search)

        if len(list_of_files_excluded_both_ids[text_to_search]["image"]) == 0:
            files_dict[text_to_search]["fails"]["from_text_filter_by_images"].append("there are no image with current name")
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

        # print(f"{_models=}")
        _models = _models.data
        # if len(_models.models) == 0:
        #     continue

        # print(text_to_search)
        # print(list_of_files_excluded_both_ids[text_to_search]["path"])

        # print(list_of_files_excluded_both_ids[text_to_search]["image"][0])

        try:
            # print(list_of_files_excluded_both_ids[text_to_search])
            filtered_models = _models.get_model_by_image(
                Path(list_of_files_excluded_both_ids[text_to_search]["path"]) / list_of_files_excluded_both_ids[text_to_search]["image"][0]
            )
            # if len(list_of_files_excluded_both_ids[text_to_search]["image"]) == 0 and _to_download_image:
            #     download_image_by_id(filtered_models[0].get_id())

            if _to_move_archives:
                archve_path = (Path(files_dict[text_to_search]["path"]) / Path(files_dict[text_to_search]["archive"][0])
                               .rename(f"{text_to_search}.{Path(files_dict[text_to_search]['path']).suffix}"))
                shutil.move(archve_path, path_to_save_directory)

            if _to_download_image:
                image_path = (Path(files_dict[text_to_search]["path"]) / Path(files_dict[text_to_search]["image"][0])
                              .rename(f"{text_to_search}.{Path(files_dict[text_to_search]['path']).suffix}"))
                shutil.move(image_path, path_to_save_directory)

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

    # print(files_dict)
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

    (
        open(f"{path_to_save_directory}/to_generate_statistic_{str(datetime.datetime.now()).split('.')[:-1][0]}.json", "w+").
        write(
            data_to_save
        )
    )
    # print(json.loads({item: files_dict[item] for item in files_dict if not files_dict[item]["status"]}))

