import time
from typing import Literal, NamedTuple

import cv2
import numpy as np
import requests
from pathlib import Path

import config
from config import PATH_TO_RESOURCES_DIRECTORY


class ImageToCompare(NamedTuple):
    image_source_type: Literal["web", "local"]
    src: str | Path

    # trash hardcode bad position
    timeout_for_request: int = 3

    @property
    def timeout(self):
        return self.timeout_for_request

    @timeout.setter
    def timeout(self, _new_timeout):
        self.timeout_for_request = _new_timeout

    def get_image_as_cv_format(self) -> cv2.typing.MatLike:
        if self.image_source_type == "web":
            _image = cv2.imdecode(
                np.asarray(
                    bytearray(requests.get(str(self.src), timeout=self.timeout_for_request).content),
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
            "equals": True if 0 <= int(err) <= 5 * diff_in_percentage and 0 <= int(mse) <= (5 * diff_in_percentage)/3 else False,
            "diff": {
                "err": err,
                "mse": mse
            }
        }


def compare_images(imageA: ImageToCompare, imageB: ImageToCompare, _debug: bool, _timeout: int) -> bool:
    _image_to_compare = ImageToCompare
    _image_to_compare.timeout_for_request = _timeout

    res = _image_to_compare.compare_images(
        imageA.get_image_as_cv_format(),
        imageB.get_image_as_cv_format()
    )

    # time.sleep(2)
    if _debug:
        print("-----"*25)
        print(f"{imageA=}")
        print(f"{imageB=}")
        print(res)
        print("-----"*25)

    return res.get("equals")



if __name__ == "__main__":
    print(
        compare_images(
            ImageToCompare(
                image_source_type="local",
                src=PATH_TO_RESOURCES_DIRECTORY / "test_data/_image_of_failes" / "Black Timber House.jpg"
            ),
            # ImageToCompare(
            #     image_source_type="local",
            #     src=PATH_TO_RESOURCES_DIRECTORY / 'test_data/Suren 2/Kitchen Appliances Kuppersberg.jpg'
            # ),
            ImageToCompare(
                "web",
                "https://b6.3ddd.ru/media/cache/sky_model_new_big_ang_en/model_images/0000/0000/0484/484442.56d2a07a64964.jpeg"
            ),
        )
    )
