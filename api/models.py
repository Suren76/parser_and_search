from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field
from typing import Optional, Literal

from search.images_compare import compare_images, ImageToCompare
from tools import get_image_url


class BaseResponseModel(BaseModel):
    status: int
    message: str
    data: BaseModel


class ModelDescriptionData(BaseModel):
    user: dict[str, object]
    platform: dict[str, object]
    render: dict[str, object] | None
    images: list
    materials: list
    colors: list
    formats: list
    form: Optional[dict[str, object]]
    type: int
    typeText: str
    title: str
    titleEn: str
    description: str
    descriptionEn: str
    slug: str
    style: str
    style_en: str
    size_kb: int
    polygons: Literal[""] | int
    length: str
    width: str
    height: str
    created: str
    version: str
    category: dict[str, object]
    subcategory: dict[str, object]
    price_free_rub: Optional[str] = None
    price_free_usd: Optional[str] = None


class ModelDescriptionResponse(BaseResponseModel):
    success: bool
    data: ModelDescriptionData
    error: list | None = None
    cache: bool

    @property
    def get_url_of_model(self) -> str:
        return "https://3dsky.org/3dmodels/show/" + self.data.slug if self.data.slug is not None else ""

    @property
    def get_account_type(self) -> str:
        return ("Pro" if self.data.type == 2 else "Free") if self.data.type is not None else ""

    @property
    def get_platform(self) -> str:
        return str(self.data.platform["titleEn"]) if self.data.platform is not None else ""

    @property
    def get_render(self) -> str:
        return str(self.data.render["title"]) if self.data.render is not None else ""

    @property
    def get_size(self) -> str:
        return str(int(self.data.size_kb/1024)) if self.data.size_kb is not None else ""

    @property
    def get_colors(self) -> str:
        return ", ".join([color["titleEn"] for color in self.data.colors]) if self.data.colors is not None else ""

    @property
    def get_style(self) -> str:
        return self.data.style_en if self.data.style_en is not None else ""

    @property
    def get_materials(self) -> str:
        return ", ".join([item["materialEn"] for item in self.data.materials]) if self.data.materials is not None else ""

    @property
    def get_formfactor(self) -> str:
        return "what is and where can i found it?"

    @property
    def get_published_date(self) -> str:
        return (
            datetime
            .strptime(self.data.created.split(" ")[0], "%Y-%m-%d")
            .strftime("%d %B %Y")
        ) if self.data.created is not None else ""

    @property
    def get_description(self) -> str:
        return ":"+self.data.descriptionEn if self.data.descriptionEn is not None else ""

    @property
    def get_category(self) -> str:
        return str(self.data.category["title_en"]) if self.data.category is not None else ""

    @property
    def get_subcategory(self) -> str:
        return str(self.data.subcategory["title_en"]) if self.data.subcategory is not None else ""

    @property
    def get_title(self) -> str:
        return self.data.titleEn if self.data.titleEn is not None else ""

    @property
    def get_url_to_image(self) -> str:
        return get_image_url(self.data.images[0]["webPath"]) if self.data.images is not None else "image_empty"

    @property
    def get_id(self):
        id_list = [
            Path(item["webPath"]).stem

            for item in self.data.images
            if item["isMain"] is True
        ]
        id_non_main = Path(self.data.images[0]["webPath"]).stem

        # print(id_list)
        return id_list[0] if len(id_list) == 1 else id_non_main if len(self.data.images) > 0 else None


class ModelTag(BaseModel):
    title: str
    multiple: int
    link: str


class ModelTagsListResponse(BaseResponseModel):
    success: bool
    data: list[ModelTag]
    error: Optional[list] = None
    cache: bool

    @property
    def get_tags(self):
        return [item.title for item in self.data]


class SearchModel(BaseModel):
    title: str
    votes_count: int
    comments_count: int
    slug: str
    title_en: str
    is_first: bool
    images: list
    category: dict[str, object]
    category_parent: dict[str, object]
    type_of_model: str = Field(alias="model_type")
    is_bookmark: bool
    is_purchase: bool
    isOwner: bool
    price: int | None = None
    price_usd: int | None = None

    def get_id(self):
        return self.images[0]["file_name"]

    def get_name(self):
        return self.title_en

    def get_images(self):
        return [image_url["web_path"] for image_url in self.images]


class SearchModelData(BaseModel):
    search_hash: str
    total_value: int
    page: int
    per_page: int
    models: list[SearchModel]
    tagsRu: list
    tagsEn: list
    backends: list[str]

    def filter_models(self, _filter: Literal["image", "id", "text"], option: str):
        if _filter == "image":
            return [
                model
                for model in self.models
                for image in model.get_images()
                if compare_images(ImageToCompare("web", get_image_url(image)), ImageToCompare("local", option))
            ]
        if _filter == "name":
            return [model for model in self.models if model.get_name() == option]
        if _filter == "id":
            return [model for model in self.models if model.get_id() == option]

    def get_model_by_image(self, _image_on_local) -> list[SearchModel]:
        for model in self.models:
            for image in model.get_images():
                if compare_images(ImageToCompare("web", get_image_url(image)), ImageToCompare("local", _image_on_local)):
                    return [model]
        return []


class SearchResponse(BaseResponseModel):
    data: SearchModelData


