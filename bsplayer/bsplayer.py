from ppadb.client import Client
from ppadb.device import Device
from bsplayer.core.bluestacks import Bluestacks
from bsplayer.core.imaging.imagefinder import TemplateImage

class Player(Bluestacks):
    def __init__(self, adb:Client, host:str, port:int):
        Bluestacks.__init__(self, adb, host, port)

    @property
    def name(self) -> str:        
        return self.address

class BluestacksPlayer:
    def __init__(self, adb_host:str='127.0.0.1', adb_port:int=5037):
        self.update_adb_address(adb_host, adb_port)
        self.players = {} #type: dict[str, Player]

    def update_adb_address(self, adb_host:str, adb_port:int):
        self._adb_host = adb_host
        self._adb_port = adb_port
        self.adb = Client(adb_host, adb_port)

    def add_player(self, device_port:str=5555) -> Player:
        player = Player(self.adb, self._adb_host, device_port)
        self.players[player.name] = player
        return player

