import time
from typing import Literal, NamedTuple

import cv2
import numpy as np
import requests

import config
from config import PATH_TO_RESOURCES_DIRECTORY


class ImageToCompare(NamedTuple):
    image_source_type: Literal["web", "local"]
    src: str

    def get_image_as_cv_format(self) -> cv2.typing.MatLike:
        if self.image_source_type == "web":
            _image = cv2.imdecode(
                np.asarray(
                    bytearray(requests.get(str(self.src)).content),
                    np.uint8
                ),
                cv2.IMREAD_COLOR
            )
        elif self.image_source_type == "local":
            _image = cv2.imread(str(self.src))
        else:
            raise Exception("ImageToCompare error")

        return _image

    @staticmethod
    def compare_images(image_a: cv2.typing.MatLike, image_b: cv2.typing.MatLike):
        size = (min(image_a.shape[0], image_b.shape[0]), min(image_a.shape[1], image_b.shape[1]))

        image_a = cv2.resize(image_a, size)
        # image_b = cv2.resize(image_b, (800, 800))
        image_b = cv2.resize(image_b, size)

        diff_in_percentage = ((size[0]*size[1])/100)
        # image_a = cv2.resize(image_a, (600, 600))
        # # image_b = cv2.resize(image_b, (800, 800))
        # image_b = cv2.resize(image_b, (600, 600))

        err = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
        err /= float(image_a.shape[0] * image_a.shape[1])
        mse = ((image_a.astype("float") - image_b.astype("float")) ** 2).mean()
        return {
            "equals": True if 0 <= int(err) <= 1 * diff_in_percentage and 0 <= int(mse) <= (1 * diff_in_percentage)/3 else False,
            "diff": {
                "err": err,
                "mse": mse
            }
        }


def compare_images(imageA: ImageToCompare, imageB: ImageToCompare):
    res = ImageToCompare.compare_images(
        imageA.get_image_as_cv_format(),
        imageB.get_image_as_cv_format()
    )

    # time.sleep(2)

    # print("-----"*25)
    # print(f"{imageA=}")
    # print(f"{imageB=}")
    # print(res)
    # print("-----"*25)

    return res.get("equals")



if __name__ == "__main__":
    print(compare_images(
        ImageToCompare(image_source_type="local", src=PATH_TO_RESOURCES_DIRECTORY/'test_data/Suren 2/Kitchen Appliances Kuppersberg.jpg'),
        # ImageToCompare(image_source_type="local", src=PATH_TO_RESOURCES_DIRECTORY/'test_data/Suren 2/Kitchen Appliances Kuppersberg.jpg'),
        ImageToCompare("web", "https://b6.3ddd.ru/media/cache/tuk_model_custom_filter_ang_en/model_images/0000/0000/1844/1844518.5ad0527829736.jpeg"),
    ))
#     # '/home/suren/Projects/upwork/maroz/parser_and_search/resources/S',
#     Path('/home/suren/Projects/upwork/maroz/parser_and_search/resources/2360.526844c5ac4c/2360.526844c5ac4c1.jpeg'),
#     # '/home/suren/Projects/upwork/maroz/parser_and_search/resources/2360.526844c5ac4c/2360.526844c5ac4c1.jpeg'
#     # '/home/suren/Projects/upwork/maroz/parser_and_search/resources/Suren/Bang & Olufsen – BeoLab 90.jpg',
#     # "https://b5.3ddd.ru/media/cache/tuk_model_custom_filter_ang_en/model_images/0000/0000/0350/350207.55ed1f2ad2b97.jpeg"
#     "
#     # '/home/suren/Projects/upwork/maroz/parser_and_search/resources/Suren/Bang & Olufsen – BeoLab 90.jpg'