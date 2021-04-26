from ppadb.client import Client
from ppadb.device import Device
from bsplayer.core.appHandler import AppHandler
from bsplayer.core.automation import Automation

class Bluestacks(Automation, AppHandler):
    def __init__(self, adb:Client, host:str, port:str):
        self._adb = adb
        self._host = host
        self._port = port
        self.adb_device = None #type: Device

    @property
    def address(self)->str:
        return f'{self._host}:{self._port}'

    def connect(self)->bool:
        if self._connect_adb_device():
            return True
        self._adb.remote_connect(self._host, self._port)
        return self._connect_adb_device()
    
    def launch_bluestacks(self):
        pass

    def _connect_adb_device(self) -> bool:
        self.adb_device = self._adb.device(self.address)
        return self.adb_device is not None

