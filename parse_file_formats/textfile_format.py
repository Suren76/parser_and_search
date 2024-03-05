from api.models import ModelDescriptionResponse, ModelTagsListResponse


def _parse_to_textfile(
    url_of_model: str,
    account_type: str,
    platform: str,
    render: str,
    size: str,
    colors: str,
    style: str,
    materials: str,
    # formfactor: str,
    published_date: str,
    description: str,
    tags: list[str],
    category: str,
    subcategory: str,
    title: str
    # url_to_rar: str,
    # url_to_image: str
):
    _url_of_model = url_of_model
    _account_type = "Buy accesses" if account_type == 2 else "Free download"
    _platform = platform
    _render = render
    _size = size
    _colors = colors
    _style = style
    _materials = materials
    # _formfactor = formfactor
    _published_date = published_date
    _description = description
    _tags = ''.join([' '+tag+':' for tag in tags])[:-1]
    _category = category
    _subcategory = subcategory
    _title = title
    # _url_to_rar = url_to_rar
    # _url_to_image = url_to_image

    string_to_write = (
        f"1: {_url_of_model}" "\n"
        f"2: {_account_type}" "\n"
        f"3: Platform: {_platform}" "\n"
        f"Render: {_render}" "\n"
        f"Size: {_size} MB" "\n"
        f"Colors: {_colors}" "\n"
        f"Style: {_style}" "\n"
        f"Materials: {_materials}" "\n"
        # f"Formfactor: {_formfactor}" "\n"
        f"Published {_published_date}" "\n"
        f"{_description}" "\n"
        f"tags: {_tags}" "\n"
        f"5: {_category}" "\n"
        f"6: {_subcategory}" "\n"
        f"7: {_title}" "\n"
        # f"{_url_to_rar}" "\n"
        # f"{_url_to_image}" "\n"
    )

    return string_to_write


def parse_response_to_textfile(model_description: ModelDescriptionResponse, tags: ModelTagsListResponse):
    return _parse_to_textfile(
        url_of_model=model_description.get_url_of_model,
        account_type=model_description.get_account_type,
        platform=model_description.get_platform,
        render=model_description.get_render,
        size=model_description.get_size,
        colors=model_description.get_colors,
        style=model_description.get_style,
        materials=model_description.get_materials,
        # formfactor=model_description.get_formfactor,
        published_date=model_description.get_published_date,
        description=model_description.get_description,
        tags=tags.get_tags,
        category=model_description.get_category,
        subcategory=model_description.get_subcategory,
        title=model_description.get_title
        # url_to_rar=model_description.get_url_to_rar,
        # url_to_image=model_description.get_url_to_image
    )
