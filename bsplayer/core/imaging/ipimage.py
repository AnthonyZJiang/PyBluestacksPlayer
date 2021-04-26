import os
from typing import Sequence, Union
import cv2
import numpy as np
import errno


class IPImage:
    def __init__(self, image: Union[str, np.ndarray], name: str = 'Unnamed'):
        self._raw_image = IPImage.load_image(
            image) if isinstance(image, str) else image
        self._processed_image = None
        self._name = name

    @property
    def raw(self) -> np.ndarray:
        return self._raw_image

    @property
    def processed(self) -> np.ndarray:
        return self._processed_image

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self) -> str:
        return self._name

    @property
    def shape(self):
        return self.raw.shape[1::-1]

    def process(self):
        raise NotImplementedError()

    def show_raw(self):
        IPImage.show(self.raw)

    def show_processed(self):
        IPImage.show(self.processed)

    @staticmethod
    def grey_image(img) -> np.ndarray:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def show(img):
        title = 'Image preview'
        cv2.namedWindow(title)
        cv2.moveWindow(title, int((1920-img.shape[1])/2), 0)
        cv2.imshow(title, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def load_image(image_path):
        if image_path is None:
            return None
        if not os.path.exists(image_path):
            raise OSError(
                errno.ENOENT, "The image path is invalid.", image_path)
        return cv2.imread(image_path)


class IPTemplate(IPImage):
    def process(self, greyscale: bool):
        if self.raw is None:
            return
        self._processed_image = IPImage.grey_image(
            self.raw) if greyscale else self.raw


class IPFrame(IPImage):

    def process(self, greyscale: bool, crop_box: Sequence[int]):
        img = self.raw if not greyscale else IPImage.grey_image(self.raw)
        self._processed_image = img if crop_box is None else IPFrame.crop_image(img, crop_box)

    def crop_image(img, box: Sequence[int]) -> np.ndarray:
        if len(img.shape) == 2:
            return img[box[1]:box[3], box[0]:box[2]].T

        ch = [img[box[1]:box[3], box[0]:box[2], i].T for i in range(img.shape[2])]
        return np.array(ch).T