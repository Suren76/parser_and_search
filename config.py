import json
from pathlib import Path
from typing import Literal
import os

MODE: Literal["single", "multiple"] = "multiple"

PATH_TO_PROJECT_FOLDR = Path(os.path.dirname(os.path.abspath(__file__)))
PATH_TO_RESOURCES_DIRECTORY = PATH_TO_PROJECT_FOLDR / "resources/"
PATH_TO_FILES_DIR = PATH_TO_RESOURCES_DIRECTORY / "Script"
PATH_TO_OUTPUT_DIRECTORY = PATH_TO_RESOURCES_DIRECTORY / "output"
TO_SAVE_FILE = PATH_TO_OUTPUT_DIRECTORY / "full.json"

PATH_TO_CATEGORIES_LIST = PATH_TO_RESOURCES_DIRECTORY / "categories_list/converted_to_.json"

CATEGORIES_LIST = {
    str(key): str(value)
    for _item in json.loads(open(PATH_TO_CATEGORIES_LIST).read()).values()
    for key, value in _item.items()
}
