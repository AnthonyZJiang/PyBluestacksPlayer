import os
from io import BytesIO
from dataclasses import dataclass
import time
from typing import Union

from ppadb.device import Device
from PIL import Image
import numpy as np
import cv2
import enum

from bsplayer.core.imaging.imageProcessor import ImageProcessor, IPParam
from bsplayer.core.imaging.ipimage import IPFrame, IPTemplate


@dataclass
class TemplateImage():
    image_path: str
    params: IPParam

    __slots__ = frozenset(__annotations__)

    def __init__(self, image_path: str, params: IPParam = None):
        self.image_path = image_path
        self.params = params

    @property
    def name(self):
        if isinstance(self.image_path, str):
            return os.path.basename(self.image_path)
        return "no-name"


class IFReturnType(enum.Enum):
    RETURN_FIRST_FOUND = 0
    RETURN_BEST_CONF = 1


@dataclass
class MultiTemplateImage():
    image_paths: list[str]
    params: IPParam
    return_type: IFReturnType

    __slots__ = frozenset(__annotations__)


class ImageFinder():
    adb_device: Device
    last_screencap_to_cv2im: np.ndarray

    def screencap(self, file_path: str = "") -> Image.Image:
        bytes = self.adb_device.screencap()
        image = Image.open(BytesIO(bytes))
        if file_path:
            image.save(file_path)
        return image

    def screencap_to_cv2im(self) -> np.ndarray:
        bytes = self.adb_device.screencap()
        self.last_screencap_to_cv2im = cv2.imdecode(np.asarray(bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        return self.last_screencap_to_cv2im

    def find_image(self, image: TemplateImage, screencap_img: np.ndarray = None) -> Union[tuple[list[tuple[int, int]], list[float]], tuple[tuple[int, int], float]]:
        screencap_img = self._get_valid_screencap(screencap_img)
        ip = ImageProcessor(IPTemplate(image.image_path, image.name),
                            IPFrame(screencap_img),
                            image.params)
        return ip.find_image()

    def find_multiple(self, images: MultiTemplateImage, screencap_img: np.ndarray = None) -> Union[tuple[tuple[int, int], float]]:
        screencap_img = self._get_valid_screencap(screencap_img)
        ip = ImageProcessor(None, IPFrame(screencap_img), images.params)
        if images.return_type == IFReturnType.RETURN_BEST_CONF:
            return self._find_multi_return_best(images.image_paths, ip)
        if images.return_type == IFReturnType.RETURN_FIRST_FOUND:
            return self._find_multi_return_first()

    def _find_multi_return_best(self, images: list[str], ip: ImageProcessor) -> Union[tuple[tuple[int, int], float]]:
        coord_best = []
        conf_best = 0
        i_best = -1
        for i, img_path in enumerate(images):
            ip.template = IPTemplate(img_path)
            coord, conf = ip.find_image()
            if conf > conf_best:
                conf_best = conf
                coord_best = coord
                i_best = i
        return coord_best, conf_best, i_best

    def _find_multi_return_first(self, images: list[str], ip: ImageProcessor) -> Union[tuple[tuple[int, int], float]]:
        for i, img_path in enumerate(images):
            ip.template = IPTemplate(img_path)
            coord, conf = ip.find_image()
            if conf > 0:
                return coord, conf, i

    def find_image_till_timeout(self, image: TemplateImage, timeout: float = 3, interval: float = 0.2):
        ip = ImageProcessor(IPTemplate(
            image.image_path, image.name), None, image.params)
        conf = 0
        sTime = time.time()
        while True:
            ip.frame = IPFrame(self.screencap_to_cv2im())
            coord, conf = ip.find_image()
            if conf or (time.time() - sTime + interval > timeout):
                return coord, conf

    def find_multiple_till_timeout(self, image: MultiTemplateImage, timeout: float = 3, interval: float = 0.2):
        raise not NotImplementedError()  # TODO implement find_multiple_till_timeout

    def _get_valid_screencap(self, screencap_img):
        return screencap_img if ImageFinder.is_valid_cv2_img(screencap_img) else self.screencap_to_cv2im()

    @staticmethod
    def is_valid_cv2_img(img):
        return isinstance(img, np.ndarray)
