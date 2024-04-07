import re
import socket
import subprocess
import shutil

from postgresql_integration_test.attributes import ConfigAttribute

BASEDIRS = ["/", "/usr", "/usr/local", "/opt/homebrew", "/usr/lib/postgresql/14"]


class Utils:
    def find_program(name):
        binary_path = shutil.which(name)
        if not binary_path:
            raise RuntimeError(f"Error, no binary {name} found!")

        return binary_path

    @staticmethod
    def get_unused_port():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 0))
        _, port = sock.getsockname()
        sock.close()

        return port

    @staticmethod
    def get_binary_version(binary_location):
        (variant, version_major, version_minor) = Utils.parse_version(
            subprocess.check_output([binary_location, "--version"]).decode(
                "utf-8"
            )
        )

        version = ConfigAttribute
        version.variant = variant
        version.major = version_major
        version.minor = version_minor

        return version

    @staticmethod
    def parse_version(version_str):
        version_info = re.findall(r"(\w+) \(PostgreSQL\) (\d+).(\d+)?", version_str)

        version_variant = None
        version_major = None
        version_minor = None
        if len(version_info) > 0:
            version_variant = version_info[0][0]
            version_major = int(version_info[0][1])
            version_minor = int(version_info[0][2])

        return (version_variant, version_major, version_minor)
