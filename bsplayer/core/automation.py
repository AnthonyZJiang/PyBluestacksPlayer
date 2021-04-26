import numpy as np
from bsplayer.core.imaging import ImageFinder, TemplateImage
from bsplayer.core.inputhandler import InputHandler

class ImageNotFoundError(Exception):
    def __init__(self, image_name):
        super().__init__(f'Fail to find image [{image_name}] on screen.')

class Automation(ImageFinder, InputHandler):

    def tap_image(self, image:TemplateImage, screencap_img:np.ndarray=None, correction:tuple=None, times:int=1, interval:float=0, sleep_timer:float=0.5, raise_error=False) -> bool:
        coord, _ = self.find_image(image, screencap_img)
        if not coord:
            if raise_error:
                raise ImageNotFoundError(image.name)
            return False
        self.input_tap(coord, correction, times, interval, sleep_timer)
        return True

    def tap_image_with_timeout(self, image:TemplateImage, timeout:float=3, find_image_interval:float=0.2, correction:tuple=(0,0), times:int=1, interval:float=0, sleep_timer:float=0.5, raise_error=False) -> bool:
        coord, _ = self.find_image_till_timeout(image, timeout, find_image_interval)
        if not coord:
            if raise_error:
                raise ImageNotFoundError(image.name)
            return False
        self.input_tap(coord, correction, times, interval, sleep_timer)
        return True