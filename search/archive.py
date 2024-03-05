import os.path
from pathlib import Path

from rarfile import RarFile

path_to_archives = Path("/home/suren/Projects/upwork/maroz/parser_and_search/resources/test_data/Suren 2")
paths_list = [
    str(path_to_archives/archive_item_path)

    for archive_item_path in os.listdir(path_to_archives)
    if ".rar" in archive_item_path
]


# print([archive.printdir()])
print(
    ([elem
        for elem in
        [
            # item_str.filename.split("/")[-1]
            [
                [{str(path_item): item_str.filename.split("/")[-1]}]

                for item_str in item

                if
                ".jpg" in item_str.filename
                or ".png" in item_str.filename
                or ".jpeg" in item_str.filename

                if item_str.filename.split("/")[-1].count(".") == 2
            ]

            for path_item in paths_list
            for item in RarFile(path_to_archives/path_item).infolist()
            # for item in [RarFile(path_to_archives/path_item).infolist() for path_item in paths_list]
            # for item_str in item

            # if
            # ".jpg" in item_str.filename
            # or ".png" in item_str.filename
            # or ".jpeg" in item_str.filename
        ]

        # if elem.count(".")==2
    ])
)
for item in paths_list:
    # print(item)
    try:
        arch_items_list_filtered_images = [
            item
            for item in RarFile(str(path_to_archives/item)).infolist()
            if
            ".jpg" in item.filename
            or ".png" in item.filename
            or ".jpeg" in item.filename
        ]
    except Exception as e:
        print("-----------------------------------------------------------------------------------------------------------------------"*5)
        print(e)
        print("-----------------------------------------------------------------------------------------------------------------------"*5)
    for arch in arch_items_list_filtered_images:
        if ".jpg" in arch.filename or ".jpeg" in arch.filename:
            # print(arch.filename)
            if "_RenderPics" in arch.filename:
                pass
                # print("_RenderPics")
            # print([arch for arch in paths_list])
# print(os.path.isdir(str(paths_list[0])))
# print(os.path.isfile(str(paths_list[0])))

# open("image.jpeg", "wb+").write(data)
