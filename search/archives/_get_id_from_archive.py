from os import PathLike

import magic

from search.archives.RarImplementation import RarImplementation
from search.archives.ZipImplementation import ZipImplementation
from search.archives.SevenZipImplementation import SevenZipImplementation


class FileNotArchive(Exception): pass


def _get_id_from_archive(path_to_archive: str | PathLike) -> str | list | None:
    __SUPPORTED_ARCHIVES_LIST = ["zip", "rar", "7z"]
    _file_type = magic.from_file(path_to_archive, mime=True).strip("/")

    if "zip" in _file_type:
        _archive = ZipImplementation(path_to_archive)
    elif "rar" in _file_type:
        _archive = RarImplementation(path_to_archive)
    elif "7z" in _file_type:
        _archive = SevenZipImplementation(path_to_archive)
    else:
        raise FileNotArchive((
            f"File not archive or not in supported archives list ({__SUPPORTED_ARCHIVES_LIST}). "
            f"file:{path_to_archive}"
        ))

    _archive_ids = _archive.get_id()

    return _archive_ids[0] \
        if len(_archive_ids) == 1 \
        else _archive_ids if len(_archive_ids) >= 2 \
        else None

