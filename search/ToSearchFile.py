import os
from pathlib import Path


class ToSearchFile:
    image: list[str]
    archive: list[str]
    unknown: list[str]
    meta: list[str]
    path: Path
    fails: dict[str, list]
    status: bool

    def __init__(
            self,
            image: list[str],
            archive: list[str],
            unknown: list[str],
            meta: list[str],
            path: str | Path,
            fails: dict[str, list],
            status: bool
    ):
        self.image = image
        self.archive = archive
        self.unknown = unknown
        self.meta = meta
        self.path = Path(path)
        self.fails = fails
        self.status = status

    @staticmethod
    def get_files_formatted_dict(self, _path_to_archives: Path):
        _files_list = {
            name: _path_to_archives / name
            for name in os.listdir(_path_to_archives)

            if ".json" not in name
        }

        # second phase
        # second_phase = [filename for filename in _files_list if filename not in _list_of_values_to_exclude]

        _list_of_class_objects = [

        ]

        filenames_list = {
            Path(file).stem.replace("_", " "): ToSearchFile(
                image=[],
                archive=[],
                unknown=[],
                meta=[],
                path=_path_to_archives,
                fails={
                    "id_as_name": [],
                    "id_from_archive": [],
                    "from_text_if_found_one_result": [],
                    "from_text_filter_by_images": []
                },
                status=False,
            )

            for file in _files_list
        }

        # print(filenames_list)

        for _item in _files_list:
            if "_" in _item:
                _old_filename = _item
                _item = _item.replace("_", " ")
                # print(_item)

                _item = Path(_path_to_archives, _old_filename).rename(
                    Path(_path_to_archives, _item)
                )
                _item = str(_item)

                # filenames_list[Path(_item).stem] = filenames_list.pop(Path(_old_filename).stem)
                filenames_list[Path(_item).stem]["meta"].append(
                    {"old_filename": _old_filename}
                )

            if ".zip" in _item or ".rar" in _item or ".7z" in _item:
                filenames_list[Path(_item).stem].archive.append(_item)
            elif ".jpeg" in _item or ".jpg" in _item or ".png" in _item:
                filenames_list[Path(_item).stem].image.append(_item)
            else:
                filenames_list[Path(_item).stem].unknown.append(_item)

        return filenames_list





