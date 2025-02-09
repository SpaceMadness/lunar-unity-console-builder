import os
import platform


class BuildPlatform:
    @staticmethod
    def unity_publish_binary() -> str:
        """
        Returns the path to the Unity editor binary used for publishing the package on the current platform.
        NOTE: The minimum supported Unity version for the package would be determined by the version of the editor.

        Returns:
            str: Path to Unity editor binary on the current platform.
        
        Raises:
            NotImplementedError: If running on an unsupported operating system.
        """
        if BuildPlatform.is_mac_os():
            return '/Applications/Unity-Publish/Unity.app/Contents/MacOS/Unity'

        elif BuildPlatform.is_windows():
            return r'C:\Program Files\Unity-Publish\Editor\Unity.exe'
        
        raise NotImplementedError("Unsupported operating system")

    @staticmethod
    def unity_log_path() -> str:
        """
        Returns the path to the Unity editor log file for the current platform.

        Returns:
            str: Path to Unity editor log file on the current platform.
        
        Raises:
            NotImplementedError: If running on an unsupported operating system.
        """
        if BuildPlatform.is_mac_os():
            return os.path.expanduser('~/Library/Logs/Unity/Editor.log')
            
        elif BuildPlatform.is_windows():
            return os.path.expanduser(r'~/AppData/Local/Unity/Editor/Editor.log')
        
        raise NotImplementedError("Unsupported operating system")

    @staticmethod
    def is_mac_os() -> bool:
        """
        Checks if the current system is macOS.

        Returns:
            bool: True if the system is macOS (returns True for both 'darwin' and 'mac'), False otherwise.
        """
        return BuildPlatform._get_system() in ('darwin', 'mac')

    @staticmethod
    def is_windows() -> bool:
        """
        Checks if the current system is Windows.

        Returns:
            bool: True if the system is Windows, False otherwise.
        """
        return BuildPlatform._get_system() == 'windows'

    @staticmethod
    def _get_system() -> str:
        """
        Gets the lowercase name of the current operating system.

        Returns:
            str: Lowercase string representing the current operating system.
        """
        return platform.system().lower()
