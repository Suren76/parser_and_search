# from typing import override

from rarfile import RarFile

from search.archives.BaseArchiveImplementation import BaseArchiveImplementation


class RarImplementation(BaseArchiveImplementation):
    # @override
    def _get_files_list(self) -> list:
        return RarFile(self._path).infolist()
