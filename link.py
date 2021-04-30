import os
import json

from platform import system

from platformio.managers.platform import PlatformBase
from platformio.util import get_systype

class P26Platform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        board = variables.get("board")
        board_config = self.board_config(board)
        build_core = variables.get("board_build.core", board_config.get("build.core", "arduino"))

        frameworks = variables.get("pioframework", [])

        if "cmsis" in frameworks:
            assert board_config.get("build.mcu", ""), ("Missing MCU field for %s" % board)
            device_package = "framework-cmsis-swm320"
            if device_package in self.packages:
                self.packages[device_package]["optional"] = False

        default_protocol = board_config.get("upload.protocol") or ""

        # configure J-LINK tool
        jlink_conds = [
            "jlink" in variables.get(option, "")
            for option in ("upload_protocol", "debug_tool")
        ]
        if board:
            jlink_conds.extend([
                "jlink" in board_config.get(key, "")
                for key in ("debug.default_tools", "upload.protocol")
            ])
        jlink_pkgname = "tool-jlink"
        if not any(jlink_conds) and jlink_pkgname in self.packages:
            del self.packages[jlink_pkgname]

        return PlatformBase.configure_default_packages(self, variables, targets)

    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_default_debug_tools(result)
        else:
            for key, value in result.items():
                result[key] = self._add_default_debug_tools(result[key])
        return result

    def _add_default_debug_tools(self, board):
        debug = board.manifest.get("debug", {})
        upload_protocols = board.manifest.get("upload", {}).get("protocols", [])
        if "tools" not in debug:
            debug['tools'] = {}

        # BlackMagic, J-Link, ST-Link
        for link in ("jlink", "stlink", "cmsis-dap"):
            if link not in upload_protocols or link in debug['tools']:
                continue
            if link == "jlink":
                assert debug.get("jlink_device"), ("Missed J-Link Device ID for %s" % board.id)
                debug['tools'][link] = {
                    "server": {
                        "package": "tool-jlink",
                        "arguments": [
                            "-singlerun",
                            "-if", "SWD",
                            "-select", "USB",
                            "-device", debug.get("jlink_device"),
                            "-port", "2331"
                        ],
                        "executable": ("JLinkGDBServerCL.exe" if system() == "Windows" else "JLinkGDBServer")
                    }
                }
            else:
                pass

            debug['tools'][link]['onboard'] = link in debug.get("onboard_tools", [])
            debug['tools'][link]['default'] = link in debug.get("default_tools", [])

        board.manifest['debug'] = debug
        return board
