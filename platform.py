import os
import platform


class Platform:
    @staticmethod
    def unity_publish():
        if Platform.is_mac_os():
            return '/Applications/Unity-Publish/Unity.app/Contents/MacOS/Unity'
        return r'C:\Program Files\Unity-Publish\Editor\Unity.exe'

    @staticmethod
    def unity_log():
        if Platform.is_mac_os():
            return os.path.expanduser('~/Library/Logs/Unity/Editor.log')
        return os.path.expanduser(r'~/AppData/Local/Unity/Editor/Editor.log')

    @staticmethod
    def is_mac_os():
        host_os = platform.system().lower()
        return 'darwin' in host_os or 'mac' in host_os
