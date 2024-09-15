from typing import Literal

from tqdm import tqdm

from api.api import API


def check_is_all_login_datas_valid(list_with_login_datas: list[dict]) -> Literal[True] | list[dict]:
    _invalid_items_list = []
    for item in tqdm(list_with_login_datas, desc="check is sessions of accounts valid"):
        valid = True
        if not API().is_phpsessid_valid(item.get("PHPSESSID")):
            valid = False
            item["PHPSESSID"] = "invalid"

        if not API().is_bearer_token_valid(item.get("BEARER_TOKEN")):
            valid = False
            item["BEARER_TOKEN"] = "invalid"

        if not valid:
            _invalid_items_list.append(item)

    if "error" in _invalid_items_list:
        raise ValueError(f"Invalid PHPSESSID is given. \n meta: {_invalid_items_list=}, {list_with_login_datas=}")
    if len(_invalid_items_list) == 0:
        return True
    else:
        return _invalid_items_list
