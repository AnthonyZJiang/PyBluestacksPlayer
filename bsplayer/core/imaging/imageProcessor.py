from typing import Sequence, Union
import cv2
import numpy as np
from bsplayer.core.imaging.ipimage import IPFrame, IPTemplate


class IPParam:
    def __init__(self, threshold: float = 0.9, multi_search_dist_threshold: int = -1, greyscale: bool = True, crop_box: Sequence[int] = None):
        self._threshold = threshold
        self._multi_search_dist_threshold = multi_search_dist_threshold
        self._greyscale = greyscale
        self._crop_box = crop_box

    @property
    def threshold(self) -> float:
        return self._threshold

    @threshold.setter
    def threshold(self, val: float):
        self._threshold = val

    @property
    def multi_search_dist_threshold(self) -> int:
        return self._multi_search_dist_threshold

    @multi_search_dist_threshold.setter
    def multi_search_dist_threshold(self, val: int):
        self._multi_search_dist_threshold = val

    @property
    def greyscale(self) -> bool:
        return self._greyscale

    @greyscale.setter
    def greyscale(self, val: bool):
        self._greyscale = val

    @property
    def crop_box(self) -> list[int]:
        return self._crop_box

    @crop_box.setter
    def crop_box(self, val: Sequence[int]):
        if val is None:
            self._crop_box = None
            return
        self._crop_box = val if isinstance(val, list) else list(val)
        self._crop_box[0] = max(self._crop_box[0], 0)
        self._crop_box[1] = max(self._crop_box[1], 0)


class ImageProcessor:
    def __init__(self, template: IPTemplate, frame: IPFrame, params: IPParam = None):
        if params is None:
            params = IPParam()
        self._params = params
        self._template = template
        self._frame = frame
        self._preprocess(template is not None, frame is not None)

    @property
    def template(self) -> IPTemplate:
        return self._template

    @template.setter
    def template(self, val: IPTemplate):
        self._template = val
        self._preprocess(True, False)

    @property
    def frame(self) -> IPFrame:
        return self._frame

    @frame.setter
    def frame(self, val: IPFrame):
        self._frame = val
        self._preprocess(False, True)

    @property
    def params(self) -> IPParam:
        return self._params

    @params.setter
    def params(self, val: IPParam):
        self._params = val
        self._preprocess(True, True)

    def find_image(self) -> Union[tuple[list[tuple[int,int]], list[float]], tuple[tuple[int,int], float]]:
        if self.template.raw is None:
            return None, 0
        match_result = cv2.matchTemplate(
            self.frame.processed,
            self.template.processed,
            cv2.TM_CCOEFF_NORMED,
        )
        width, height = self.template.shape

        if self.params.multi_search_dist_threshold > -1:
            raise not NotImplementedError() #TODO to implement multi match, non-maximum suppression
        else:
            return self._get_best_coords(match_result, width, height)

    def _preprocess(self, template: bool, frame: bool):
        if template:
            self.template.process(self.params.greyscale)
        if frame:
            self.frame.process(self.params.greyscale, self.params.crop_box)

    def _get_best_coords(self, match_result, width, height) -> tuple[tuple[int,int], float]:
        _, conf, _, max_loc = cv2.minMaxLoc(match_result)

        if conf < self.params.threshold:
            return None, 0
        return self._loc_to_coords(max_loc, width, height), conf

    def _loc_to_coords(self, loc, width, height) -> tuple[int, int]:
        correction = [0, 0]
        if self.params.crop_box is not None:
            correction = self.params.crop_box[0:2]
        return loc[0]+width//2+correction[0], loc[1]+height//2+correction[1]
