import re

class BaseArchiveImplementation:
    _re: re = __import__("re")
    _path: str

    def __init__(self, path):
        self._path = path

    def get_id(self):
        return [
            _filename

            for _filename in self._get_images_of_archive()

            if _filename.count(".") == 2
            if self._re.match("\d{7}.[a-z\d]{13}.", _filename) is not None
        ]

    def _get_images_of_archive(self):
        return [
            item_str.filename.split("/")[-1]

            for item_str in self._get_files_list()

            if
            ".jpg" in item_str.filename
            or ".png" in item_str.filename
            or ".jpeg" in item_str.filename
        ]

    def _get_files_list(self) -> list:
        ...
