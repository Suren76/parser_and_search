# from typing import override
from zipfile import ZipFile


from search.archives.BaseArchiveImplementation import BaseArchiveImplementation


class ZipImplementation(BaseArchiveImplementation):
    # @override
    def _get_files_list(self) -> list:
        return ZipFile(self._path).infolist()
