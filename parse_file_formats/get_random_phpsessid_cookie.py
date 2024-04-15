def get_random_phpsessid_cookie(_list_with_phpsessids: list[dict]) -> str:
    import random
    return f"PHPSESSID={random.choice(_list_with_phpsessids).get('PHPSESSID')};"
