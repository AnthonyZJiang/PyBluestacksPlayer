from typing import Union, TypedDict
from ppadb.device import Device
import re


class DumpedApp(TypedDict):
    raw: str
    package_name: str
    activity_name: str


class AppHandler:
    adb_device: Device

    def is_app_foreground(self, app_package_name: str, app_activity_name: str = "") -> bool:
        result = self.dump_foreground_app()
        return result.find(f'{app_package_name}/{app_activity_name}') != -1

    def run_app(self, app_package_name: str, app_activity_name: str):
        self.adb_device.shell(
            f'am start -n {app_package_name}/{app_activity_name}')

    def kill_app(self, app_package_name: str):
        self.adb_device.shell(f'am force-stop {app_package_name}')

    def dump_foreground_app(self, output_to_dict: bool = False) -> Union[str, DumpedApp]:
        res = self.adb_device.shell(
            'dumpsys window windows | grep mCurrentFocus')
        if not output_to_dict:
            return res
        pattern = re.compile(r'.+{(.*) (.*) (.*)/(.*)}')
        match = pattern.match(res)
        if match:
            return {'raw': res,
                    'package_name': match.group(3),
                    'activity_name': match.group(4)}
        return {'raw': res, 'package_name': '', 'activity_name': ''}

    def is_app_installed(self, app_package_name: str) -> bool:
        self.adb_device.shell(f'pm list packages [{app_package_name}]')

    def install_app(self, app_package_location: str) -> bool:
        pass
