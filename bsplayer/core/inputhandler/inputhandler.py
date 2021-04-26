import base64
from bsplayer.core import inputhandler
from time import sleep
from typing import Sequence, Union
from ppadb.device import Device

from bsplayer.core.inputhandler.keycode import KeyCode

class InputHandler:
    adb_device: Device

    def input_tap(self, coord:Sequence[int], correction:Sequence[int]=None, times:int=1, interval:float=0, sleep_timer:float=0.5):
        if correction:
            coord = (coord[0]+correction[0], coord[1]+correction[1])
        self._input_tap_xy(coord[0], coord[1], times, interval)
        if sleep_timer:
            sleep(sleep_timer)

    def input_swipe(self, x0, y0, x1, y1, duration=500, sleep_timer:float=0.5):
        self.adb_device.shell(f'input swipe {x0} {y0} {x1} {y1} {duration}')
        if sleep_timer:
            sleep(sleep_timer)

    def input_long_press(self, x, y, duration, sleep_timer:float=0.5):
        self.adb_device.shell(f'input swipe {x} {y} {x} {y} {duration}')
        if sleep_timer:
            sleep(sleep_timer)

    def input_roll(self, x, y, sleep_timer:float=0.5):
        self.adb_device.shell(f'input roll {x} {y}')
        if sleep_timer:
            sleep(sleep_timer)

    def input_text(self, text:str, sleep_timer:float=0.5):
        text.replace(' ','%s')
        self.adb_device.shell(f'input text {text}')
        if sleep_timer:
            sleep(sleep_timer)

    def input_text_unicode(self, text:str, sleep_timer:float=0.5):
        self.adb_device.shell('ime set com.android.adbkeyboard/.AdbIME')
        charsb64 = str(base64.b64encode(text.encode('utf-8')))[1:]
        self.adb_device.shell(f'am broadcast -a ADB_INPUT_B64 --es msg {charsb64}')
        self.adb_device.shell('ime set com.android.inputmethod.latin/.LatinIME')
        if sleep_timer:
            sleep(sleep_timer)

    def input_keyevent(self, key: Union[int, KeyCode], sleep_timer:float=0.5):
        if isinstance(key, KeyCode):
            key = key.value
        self.adb_device.shell(f'input keyevent {key}')
        if sleep_timer:
            sleep(sleep_timer)

    def _input_tap_xy(self, x:int, y:int, times:int=1, interval:float=0):
        if times > 1:
            self._input_tap_xy_repeat(x, y, times, interval)
        else:
            self.adb_device.shell(f'input tap {x} {y}')

    def _input_tap_xy_repeat(self, x:int, y:int, times:int=2, interval=0):
        input_cmd = f'input tap {x} {y};'
        cmd_ = input_cmd if interval <= 0 else input_cmd + f'sleep {interval};'
        cmd_final = "".join(cmd_ for _ in range(times-1))
        cmd_final += input_cmd
        self.adb_device.shell(cmd_final)
