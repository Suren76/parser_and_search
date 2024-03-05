# from typing import override

from py7zr import SevenZipFile

from search.archives.BaseArchiveImplementation import BaseArchiveImplementation



class SevenZipImplementation(BaseArchiveImplementation):
    # @override
    def _get_files_list(self) -> list:
        return SevenZipFile(self._path).list()
