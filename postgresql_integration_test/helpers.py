import re
import socket

BASEDIRS = ["/", "/usr", "/usr/local", "/opt/homebrew"]


class Utils:
    @staticmethod
    def get_unused_port():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 0))
        _, port = sock.getsockname()
        sock.close()

        return port

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
