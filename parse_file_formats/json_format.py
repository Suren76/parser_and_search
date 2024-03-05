from pydantic import BaseModel

from api.models import ModelDescriptionResponse, ModelTagsListResponse
from config import CATEGORIES_LIST


class AttributeItem(BaseModel):
    id: int
    name: str
    options: list[str]


class DownloadItem(BaseModel):
    name: str
    file: str


class ItemBaseModel(BaseModel):
    name: str
    type: str
    regular_price: str
    description: str
    short_description: str
    # sku: str
    # categories: list[dict[str, str]]
    # tags: list[dict[str, str]]
    # images: list[dict[str, str]]
    # attributes: list[AttributeItem]


class ItemProModel(ItemBaseModel):
    sku: str
    categories: list[dict[str, str]]
    downloadable: bool
    downloads: list[DownloadItem]
    tags: list[dict[str, str]]
    images: list[dict[str, str]]
    attributes: list[AttributeItem]

    type: str = "simple"
    regular_price: str = "2"


class ItemFreeModel(ItemBaseModel):
    external_url: str
    sku: str
    categories: list[dict[str, str]]
    tags: list[dict[str, str]]
    images: list[dict[str, str]]
    attributes: list[AttributeItem]
    button_text: str = "Download"  #  arje?

    type: str = "external"
    regular_price: str = "0"


class CategoryItem:
    _CATEGORIES_LIST = CATEGORIES_LIST

    id: int = None
    name: str = None

    def __init__(self, _name):
        if _name in self._CATEGORIES_LIST:
            self.id = self._CATEGORIES_LIST.get(_name)
        else:
            self.name = _name

    @property
    def dict(self):
        return {"id": self.id} if self.id is not None else {"name": self.name}


def _get_item(
        item_type: str,
        name: str,
        description: str,
        short_description: str,
        sku: str,
        categories: list[CategoryItem],
        image_url: str,
        tags: list[dict[str, str]],
        attributes: list[AttributeItem],
        file_url: str
) -> ItemBaseModel:
    _image_block = [{"src": image_url}]
    _file_url: str = file_url

    if item_type == "Free":
        return ItemFreeModel(
            name=name,
            description=description,
            short_description=short_description,
            sku=sku,
            categories=categories,
            images=_image_block,
            tags=tags,
            attributes=attributes,

            external_url=file_url
        )
    elif item_type == "Pro":
        return ItemProModel(
            name=name,
            description=description,
            short_description=short_description,
            categories=categories,

            sku=sku,
            images=_image_block,
            tags=tags,
            attributes=attributes,

            downloads=[DownloadItem(name=sku, file=_file_url)],
            downloadable=True
        )


def get_item_from_response(model_description: ModelDescriptionResponse, tags: ModelTagsListResponse):
    _short_description_raw = {
        "Platform": model_description.get_platform,
        "Render": model_description.get_render,
        "Size": model_description.get_size,
        "Style": model_description.get_style,
        "Materials": model_description.get_materials
    }

    _account_type: str = model_description.get_account_type
    _name: str = model_description.get_title
    _filename = model_description.data.images[0]["webPath"].split("/")[-1].split(".jpeg")[0]
    _description: str = model_description.get_description
    _categories: list[CategoryItem] = [CategoryItem(model_description.data.subcategory["title_en"]).dict]
    _image_url: str = model_description.get_url_to_image
    _file_url: str = model_description.get_url_to_rar #  "file_url_not_set (archive)"

    _short_description: str = "".join([
        f"{key}:\t{value}\n"
        for key, value in _short_description_raw.items()
        if type(value) is str and len(value)
    ])[:-1]
    _tags: list[dict[str, str]] = (
        [
            {"name": str(tag.strip())}

            for tag in tags.get_tags
        ] if len(tags.data) > 0 else [{"name": ""}]
    )

    _attributes: list[AttributeItem] = [
        AttributeItem(id=1, name="Price", options=[_account_type]),
        AttributeItem(id=2, name="Render", options=[model_description.get_render]),
        AttributeItem(id=3, name="Style", options=[model_description.get_style])
    ]

    return _get_item(
        item_type=_account_type,
        name=_name,
        description=_description,
        short_description=_short_description,
        sku=_filename,
        categories=_categories,
        image_url=_image_url,
        file_url=_file_url,
        tags=_tags,
        attributes=_attributes
    )
