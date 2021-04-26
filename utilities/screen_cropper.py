import cv2
import numpy as np
from bsplayer.core.imaging.ipimage import IPFrame
from bsplayer import BluestacksPlayer

max_window_size = [1920, 1000]
min_window_size = [800, 800]

def auto_scale(img:np.array) -> tuple[np.array, float]:
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
    w_new = r* min_window_size[1]
    if w_new <= max_window_size[0]:
        return min_window_size[1]/h
    return max_window_size[0]/w

def get_shrink_to_max_size_scale_factor(h, w):
    return max_window_size[1]/h if h>w else max_window_size[0]/w
    
def get_roi_and_crop(img) -> IPFrame:
    ipf = IPFrame(img)
    img, scaling_factor = auto_scale(img)
    r = cv2.selectROI('select', img)
    cv2.destroyWindow('select')
    if (r[2]-r[0] == 0) or (r[3]-r[1] == 0):
        exit()
    box = (int(round(r[0]/scaling_factor)), int(round(r[1]/scaling_factor)), int(round((r[0]+r[2])/scaling_factor)), int(round((r[1]+r[3])/scaling_factor)))
    ipf.process(False, box)
    return ipf

def save_and_exit(img):
    ans = input('Enter a filename: *.png\n')
    cv2.imwrite(f'{ans}.png', img)
    exit()


bp = BluestacksPlayer()
player = bp.add_player()
player.connect()
im = player.screencap_to_cv2im()

ipf = get_roi_and_crop(im)
ipf.show_processed()
ans = input('Do you want to crop the image again? Y/N\n')
if ans.lower() != 'y':
    save_and_exit(ipf.processed)

ipf = get_roi_and_crop(ipf.processed)
ipf.show_processed()
save_and_exit(ipf.processed)