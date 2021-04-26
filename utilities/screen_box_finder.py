import cv2
import numpy as np
import pyperclip
from bsplayer.core.imaging.ipimage import IPFrame
from bsplayer import BluestacksPlayer

max_window_size = [1920, 1000]
min_window_size = [800, 800]


def auto_scale(img: np.array) -> tuple[np.array, float]:
    s = img.shape
    h = s[0]
    w = s[1]
    if (h < min_window_size[1]) or (w < min_window_size[0]):
        factor = get_expand_to_min_size_scale_factor(h, w)
    elif (h > max_window_size[1]) or (w > max_window_size[0]):
        factor = get_shrink_to_max_size_scale_factor(h, w)
    else:
        return img, 1
    w = int(w*factor)
    h = int(h*factor)
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA), factor


def get_expand_to_min_size_scale_factor(h, w):
    r = h/w
    if r > 1:
        h_new = r * min_window_size[0]
        if h_new <= max_window_size[1]:
            return min_window_size[0]/w
        return max_window_size[1]/h
    w_new = r * min_window_size[1]
    if w_new <= max_window_size[0]:
        return min_window_size[1]/h
    return max_window_size[0]/w


def get_shrink_to_max_size_scale_factor(h, w):
    return max_window_size[1]/h if h > w else max_window_size[0]/w


def get_roi_and_crop(img) -> tuple[int, int, int, int]:
    img, scaling_factor = auto_scale(img)
    r = cv2.selectROI('select', img)
    cv2.destroyWindow('select')
    if r:
        r = (
            int(round(r[0] / scaling_factor)),
            int(round(r[1] / scaling_factor)),
            int(round((r[0] + r[2]) / scaling_factor)),
            int(round((r[1] + r[3]) / scaling_factor)),
        )
    return r


bp = BluestacksPlayer()
player = bp.add_player()
player.connect()
im = player.screencap_to_cv2im()
while True:
    box = get_roi_and_crop(im)
    if not box:
        print('Canceled.')
    else:
        print('Data has been copied:', box)
        pyperclip.copy(str(box))
    input('Press Enter to find a new box...')