def _update_env_variable(_list: list):
    import os, json
    os.environ["LIST_OF_ACTUAL_LOGIN_DATAS"] = json.dumps(_list)
    path_to_envfile = os.environ.get("PATH_TO_ENVFILE")
    file = open(path_to_envfile, "w+")
    file.seek(0)
    file.write(
        f"LIST_OF_ACTUAL_LOGIN_DATAS={json.dumps(_list)}" + "\n"
    )
    file.close()


def get_random_bearer_token(_list_with_jwts: list[dict]):
    from api.api import API
    import random
    item = random.choice(_list_with_jwts)
    bearer_token = item.get('BEARER_TOKEN')
    refresh_token = item.get('REFRESH_TOKEN')

    if not API().is_bearer_token_valid(bearer_token):
        _res = API().get_bearer_token(refresh_token)
        bearer_token = _res.get('token')
        if not refresh_token == _res.get("refresh_token"):
            refresh_token = _res.get("refresh_token")
            _item_index = _list_with_jwts.index(item)
            _list_with_jwts[_item_index].update({
                "BEARER_TOKEN": bearer_token,
                "REFRESH_TOKEN": refresh_token
            })
            _update_env_variable(_list_with_jwts)

    return f"Bearer {bearer_token}"
