import os
from time import sleep

import config
from api.models import SearchModelData
from search.search_on_web import get_slug_of_model_by_text
from parse_file_formats.parse_file_formats import get_textfile

path_to_archives = "resources/test_data/Suren 2"

files_list = [name for name in os.listdir(path_to_archives)] + [name for name in os.listdir(path_to_archives[:-2])]
ids_list = [name for name in files_list if name.count(".") == 2]


ids_list_filtered_singles = [_id for _id in set(ids_list) if ids_list.count(_id) == 2]

# print(ids_list_filtered_singles)
# print(len(ids_list_filtered_singles))

second_phase = [filename for filename in files_list if filename not in ids_list]

def get_files_with_one_search_result():
    for _id_filename in ids_list_filtered_singles:
        _slug = get_slug_of_model_by_text(_id_filename)

        if type(_slug) == dict:
            if _slug.get("message") == "there is more than one model":
                # print(_id_filename)
                second_phase.append({_id_filename: _slug.get("models")})
                continue

        # get_textfile(_slug)

        (
            open(config.PATH_TO_OUTPUT_DIRECTORY / f"{_id_filename}.txt", "w+")
            .write(get_textfile(get_slug_of_model_by_text(_id_filename)))
        )

print("first phase ends")

sleep(3)

print("-----------------------------------------------"*7)
print("-----------------------------------------------"*7)

print(second_phase)

third_phase = []
for _id_filename_second_phase in second_phase:
    _image_name = list(_id_filename_second_phase.items())[0][0]
    _image_path = [
        file_name
        for file_name in files_list
        if not (".rar" in file_name or ".zip" in file_name) and _image_name in file_name
    ][0]

    print(_image_path)
    print(path_to_archives+"/"+_image_path)

    _models: SearchModelData = list(_id_filename_second_phase.items())[0][1]
    filtered_models = _models.filter_models("image", path_to_archives+"/"+_image_path)
    print(f"{filtered_models=}")
    # _slug = get_slug_of_model_by_text(_id_filename)


    # if type(_slug) == dict:
    #     if _slug.get("message") == "there is more than one model":
    #         print(_id_filename)
    #         second_phase.append(_id_filename)
    #         continue
