from typing import Literal

from tqdm import tqdm

from api.api import API


def check_is_all_phpsessids_valid(list_with_phpsessids: list[dict]) -> Literal[True] | list[dict]:
    _invalid_items_list = []
    for item in tqdm(list_with_phpsessids, desc="check is sessions of accounts valid"):
        if not API().is_phpsessid_valid(item.get("PHPSESSID")):
            _invalid_items_list.append(item)

    if "error" in _invalid_items_list:
        raise ValueError(f"Invalid PHPSESSID is given. \n meta: {_invalid_items_list=}, {list_with_phpsessids=}")
    if len(_invalid_items_list) == 0:
        return True
    else:
        return _invalid_items_list
