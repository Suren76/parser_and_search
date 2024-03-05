class BaseArchiveImplementation:
    _path: str

    def __init__(self, path):
        self._path = path

    def get_id(self):
        return [
            _filename

            for _filename in self._get_images_of_archive()

            if _filename.count(".") == 2
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
