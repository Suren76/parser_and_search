def get_bearer_token_auth(_list_with_phpsessids: list[dict]) -> str:
    import random
    return f"Bearer {random.choice(_list_with_phpsessids).get('BEARER_TOKEN')};"
